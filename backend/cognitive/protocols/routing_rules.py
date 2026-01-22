"""
Routing Rules for Protocol Standardization

Intelligent routing rules for cognitive engine requests.
Implements PROMPT 78 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from .discovery import ServiceDiscovery, ServiceType
from .messages import AgentMessage, MessageFormat, MessageType


class RuleType(Enum):
    """Types of routing rules."""

    CONTENT_BASED = "content_based"
    CAPABILITY_BASED = "capability_based"
    WORKLOAD_BASED = "workload_based"
    PRIORITY_BASED = "priority_based"
    ROUND_ROBIN = "round_robin"
    AFFINITY = "affinity"
    GEOGRAPHIC = "geographic"
    CUSTOM = "custom"


class RuleAction(Enum):
    """Actions for routing rules."""

    ROUTE_TO = "route_to"
    REJECT = "reject"
    TRANSFORM = "transform"
    SPLIT = "split"
    MERGE = "merge"
    CACHE = "cache"
    RATE_LIMIT = "rate_limit"
    LOG = "log"


class RulePriority(Enum):
    """Priority levels for routing rules."""

    LOWEST = 0
    LOW = 25
    NORMAL = 50
    HIGH = 75
    HIGHEST = 100


@dataclass
class RoutingRule:
    """A routing rule definition."""

    rule_id: str
    name: str
    description: str
    rule_type: RuleType
    priority: RulePriority
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    enabled: bool
    match_count: int = 0
    last_matched: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize rule ID."""
        if not self.rule_id:
            self.rule_id = str(uuid.uuid4())

    def matches(self, request_data: Dict[str, Any]) -> bool:
        """Check if rule matches request data."""
        for condition in self.conditions:
            if not self._evaluate_condition(condition, request_data):
                return False
        return True

    def _evaluate_condition(
        self, condition: Dict[str, Any], request_data: Dict[str, Any]
    ) -> bool:
        """Evaluate a single condition."""
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        if not field or not operator:
            return False

        # Get field value from request data
        field_value = self._get_field_value(request_data, field)

        if field_value is None:
            return False

        # Evaluate based on operator
        if operator == "equals":
            return field_value == value
        elif operator == "not_equals":
            return field_value != value
        elif operator == "contains":
            return str(value).lower() in str(field_value).lower()
        elif operator == "not_contains":
            return str(value).lower() not in str(field_value).lower()
        elif operator == "starts_with":
            return str(field_value).lower().startswith(str(value).lower())
        elif operator == "ends_with":
            return str(field_value).lower().endswith(str(value).lower())
        elif operator == "regex":
            try:
                return bool(re.search(str(value), str(field_value)))
            except:
                return False
        elif operator == "in":
            return field_value in value if isinstance(value, (list, set)) else False
        elif operator == "not_in":
            return field_value not in value if isinstance(value, (list, set)) else True
        elif operator == "greater_than":
            try:
                return float(field_value) > float(value)
            except:
                return False
        elif operator == "less_than":
            try:
                return float(field_value) < float(value)
            except:
                return False
        elif operator == "exists":
            return field in request_data and request_data[field] is not None
        elif operator == "not_exists":
            return field not in request_data or request_data[field] is None

        return False

    def _get_field_value(self, data: Dict[str, Any], field: str) -> Any:
        """Get field value using dot notation."""
        keys = field.split(".")
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value


@dataclass
class RoutingResult:
    """Result of routing evaluation."""

    matched_rules: List[RoutingRule]
    selected_agent: Optional[str]
    actions: List[Dict[str, Any]]
    transformed_data: Optional[Dict[str, Any]]
    rejected: bool
    rejection_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class RoutingEngine:
    """
    Intelligent routing rules for cognitive engine requests.

    Manages rule evaluation and agent selection.
    """

    def __init__(self, service_discovery: ServiceDiscovery = None):
        """
        Initialize the routing engine.

        Args:
            service_discovery: Service discovery instance
        """
        self.service_discovery = service_discovery

        # Rule registry
        self.rules: List[RoutingRule] = []
        self.rule_index: Dict[str, List[RoutingRule]] = {}  # rule_type -> rules

        # Agent load balancing
        self.agent_loads: Dict[str, Dict[str, Any]] = {}
        self.round_robin_counters: Dict[str, int] = {}

        # Affinity tracking
        self.affinity_groups: Dict[str, Set[str]] = {}

        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_routes": 0,
            "rejected_requests": 0,
            "rules_matched": 0,
            "rules_by_type": {},
            "average_evaluation_time_ms": 0.0,
        }

        # Setup default rules
        self._setup_default_rules()

    def add_rule(self, rule: RoutingRule) -> None:
        """Add a routing rule."""
        self.rules.append(rule)

        # Update index
        rule_type = rule.rule_type.value
        if rule_type not in self.rule_index:
            self.rule_index[rule_type] = []
        self.rule_index[rule_type].append(rule)

        # Sort rules by priority
        self.rules.sort(key=lambda r: r.priority.value, reverse=True)
        self.rule_index[rule_type].sort(key=lambda r: r.priority.value, reverse=True)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a routing rule."""
        for i, rule in enumerate(self.rules):
            if rule.rule_id == rule_id:
                # Remove from index
                rule_type = rule.rule_type.value
                if rule_type in self.rule_index:
                    self.rule_index[rule_type].remove(rule)

                # Remove from main list
                self.rules.remove(rule)
                return True
        return False

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a routing rule."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                rule.enabled = True
                return True
        return False

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a routing rule."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                rule.enabled = False
                return True
        return False

    async def route_request(
        self, request_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> RoutingResult:
        """
        Route a request to appropriate agent.

        Args:
            request_data: Request data
            context: Routing context

        Returns:
            Routing result
        """
        start_time = datetime.now()

        try:
            # Evaluate rules
            matched_rules = []

            for rule in self.rules:
                if not rule.enabled:
                    continue

                if rule.matches(request_data):
                    matched_rules.append(rule)
                    rule.match_count += 1
                    rule.last_matched = datetime.now()

            # Update statistics
            self.stats["total_requests"] += 1
            self.stats["rules_matched"] += len(matched_rules)

            # Process matched rules
            if not matched_rules:
                # No rules matched, use default routing
                result = await self._default_routing(request_data, context)
            else:
                result = await self._process_rules(matched_rules, request_data, context)

            # Update statistics
            evaluation_time_ms = int(
                (datetime.now() - start_time).total_seconds() * 1000
            )
            total_requests = self.stats["total_requests"]
            current_avg = self.stats["average_evaluation_time_ms"]
            self.stats["average_evaluation_time_ms"] = (
                current_avg * (total_requests - 1) + evaluation_time_ms
            ) / total_requests

            if result.rejected:
                self.stats["rejected_requests"] += 1
            else:
                self.stats["successful_routes"] += 1

            return result

        except Exception as e:
            return RoutingResult(
                matched_rules=[],
                selected_agent=None,
                actions=[],
                transformed_data=None,
                rejected=True,
                rejection_reason=f"Routing error: {str(e)}",
                metadata={"error": str(e)},
            )

    async def _process_rules(
        self,
        matched_rules: List[RoutingRule],
        request_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> RoutingResult:
        """Process matched routing rules."""
        actions = []
        selected_agent = None
        transformed_data = request_data.copy()
        rejected = False
        rejection_reason = ""

        for rule in matched_rules:
            # Process actions
            for action in rule.actions:
                action_type = action.get("type")

                if action_type == RuleAction.ROUTE_TO.value:
                    selected_agent = await self._select_agent(
                        action.get("agent"),
                        action.get("strategy", "load_balance"),
                        request_data,
                        context,
                    )

                elif action_type == RuleAction.REJECT.value:
                    rejected = True
                    rejection_reason = action.get("reason", "Request rejected by rule")

                elif action_type == RuleAction.TRANSFORM.value:
                    transformed_data = await self._transform_data(
                        transformed_data, action.get("transformations", [])
                    )

                elif action_type == RuleAction.SPLIT.value:
                    # Handle request splitting
                    pass

                elif action_type == RuleAction.MERGE.value:
                    # Handle request merging
                    pass

                elif action_type == RuleAction.CACHE.value:
                    # Handle caching
                    pass

                elif action_type == RuleAction.RATE_LIMIT.value:
                    # Handle rate limiting
                    pass

                elif action_type == RuleAction.LOG.value:
                    # Handle logging
                    pass

                actions.append(action)

        return RoutingResult(
            matched_rules=matched_rules,
            selected_agent=selected_agent,
            actions=actions,
            transformed_data=transformed_data,
            rejected=rejected,
            rejection_reason=rejection_reason,
            metadata={
                "rules_evaluated": len(matched_rules),
                "processing_time": datetime.now().isoformat(),
            },
        )

    async def _default_routing(
        self, request_data: Dict[str, Any], context: Dict[str, Any] = None
    ) -> RoutingResult:
        """Default routing when no rules match."""
        # Try to route based on request type
        request_type = request_data.get("request_type", "general")

        if self.service_discovery:
            # Find agents with matching capability
            services = self.service_discovery.discover_by_capability(request_type)

            if services:
                # Select least loaded agent
                selected_agent = await self._select_agent(
                    [s.service_id for s in services],
                    "load_balance",
                    request_data,
                    context,
                )

                return RoutingResult(
                    matched_rules=[],
                    selected_agent=selected_agent,
                    actions=[],
                    transformed_data=request_data,
                    rejected=False,
                    rejection_reason="",
                    metadata={"routing_method": "default_capability_based"},
                )

        # No suitable agent found
        return RoutingResult(
            matched_rules=[],
            selected_agent=None,
            actions=[],
            transformed_data=request_data,
            rejected=True,
            rejection_reason="No suitable agent found",
            metadata={"routing_method": "default_failed"},
        )

    async def _select_agent(
        self,
        agents: Union[str, List[str]],
        strategy: str,
        request_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """Select an agent based on strategy."""
        if isinstance(agents, str):
            agents = [agents]

        if not agents:
            return None

        strategy = strategy.lower()

        if strategy == "round_robin":
            return self._round_robin_selection(agents)
        elif strategy == "load_balance":
            return self._load_balance_selection(agents)
        elif strategy == "affinity":
            return self._affinity_selection(agents, request_data, context)
        elif strategy == "random":
            return self._random_selection(agents)
        else:
            # Default to first agent
            return agents[0]

    def _round_robin_selection(self, agents: List[str]) -> str:
        """Select agent using round-robin strategy."""
        # Use first agent as key for round-robin
        key = agents[0] if agents else "default"

        if key not in self.round_robin_counters:
            self.round_robin_counters[key] = 0

        counter = self.round_robin_counters[key]
        self.round_robin_counters[key] = (counter + 1) % len(agents)

        return agents[counter]

    def _load_balance_selection(self, agents: List[str]) -> str:
        """Select agent with lowest load."""
        min_load = float("inf")
        selected_agent = None

        for agent in agents:
            load = self.agent_loads.get(agent, {}).get("current_load", 0)
            if load < min_load:
                min_load = load
                selected_agent = agent

        return selected_agent or agents[0]

    def _affinity_selection(
        self, agents: List[str], request_data: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """Select agent based on affinity."""
        # Check for existing affinity groups
        user_id = context.get("user_id") or request_data.get("user_id")
        session_id = context.get("session_id") or request_data.get("session_id")

        if user_id and user_id in self.affinity_groups:
            # Find agent with affinity for this user
            user_agents = self.affinity_groups[user_id]
            for agent in agents:
                if agent in user_agents:
                    return agent

        if session_id and session_id in self.affinity_groups:
            # Find agent with affinity for this session
            session_agents = self.affinity_groups[session_id]
            for agent in agents:
                if agent in session_agents:
                    return agent

        # No affinity found, use load balancing
        return self._load_balance_selection(agents)

    def _random_selection(self, agents: List[str]) -> str:
        """Select agent randomly."""
        import random

        return random.choice(agents)

    async def _transform_data(
        self, data: Dict[str, Any], transformations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Transform request data."""
        transformed = data.copy()

        for transform in transformations:
            transform_type = transform.get("type")

            if transform_type == "add_field":
                field = transform.get("field")
                value = transform.get("value")
                if field:
                    transformed[field] = value

            elif transform_type == "remove_field":
                field = transform.get("field")
                if field in transformed:
                    del transformed[field]

            elif transform_type == "update_field":
                field = transform.get("field")
                value = transform.get("value")
                if field and field in transformed:
                    transformed[field] = value

            elif transform_type == "rename_field":
                old_field = transform.get("old_field")
                new_field = transform.get("new_field")
                if old_field in transformed and new_field:
                    transformed[new_field] = transformed.pop(old_field)

        return transformed

    def update_agent_load(self, agent_id: str, load: float) -> None:
        """Update agent load information."""
        if agent_id not in self.agent_loads:
            self.agent_loads[agent_id] = {}

        self.agent_loads[agent_id]["current_load"] = load
        self.agent_loads[agent_id]["last_updated"] = datetime.now()

    def add_affinity(self, group_key: str, agent_id: str) -> None:
        """Add agent to affinity group."""
        if group_key not in self.affinity_groups:
            self.affinity_groups[group_key] = set()

        self.affinity_groups[group_key].add(agent_id)

    def remove_affinity(self, group_key: str, agent_id: str) -> bool:
        """Remove agent from affinity group."""
        if group_key in self.affinity_groups:
            if agent_id in self.affinity_groups[group_key]:
                self.affinity_groups[group_key].remove(agent_id)
                if not self.affinity_groups[group_key]:
                    del self.affinity_groups[group_key]
                return True
        return False

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        return self.stats

    def get_rule_stats(self) -> Dict[str, Any]:
        """Get rule statistics."""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules if r.enabled]),
            "rules_by_type": {
                rule_type: len(rules) for rule_type, rules in self.rule_index.items()
            },
            "most_matched_rules": sorted(
                [(r.rule_id, r.match_count) for r in self.rules],
                key=lambda x: x[1],
                reverse=True,
            )[:10],
        }

    def get_agent_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "agent_loads": self.agent_loads,
            "affinity_groups": {
                group_key: list(agents)
                for group_key, agents in self.affinity_groups.items()
            },
            "round_robin_counters": self.round_robin_counters,
        }

    def _setup_default_rules(self) -> None:
        """Setup default routing rules."""
        # Content-based routing rules
        content_rule = RoutingRule(
            rule_id="content_text_processing",
            name="Text Processing Routing",
            description="Route text processing requests",
            rule_type=RuleType.CONTENT_BASED,
            priority=RulePriority.HIGH,
            conditions=[
                {"field": "content_type", "operator": "equals", "value": "text"},
                {"field": "request_type", "operator": "equals", "value": "processing"},
            ],
            actions=[
                {"type": RuleAction.ROUTE_TO.value, "agent": "text_processor"},
                {
                    "type": RuleAction.LOG.value,
                    "message": "Text processing request routed",
                },
            ],
            enabled=True,
        )

        # Capability-based routing rules
        capability_rule = RoutingRule(
            rule_id="capability_perception",
            name="Perception Capability Routing",
            description="Route to perception module",
            rule_type=RuleType.CAPABILITY_BASED,
            priority=RulePriority.HIGHEST,
            conditions=[
                {
                    "field": "required_capabilities",
                    "operator": "contains",
                    "value": "perception",
                }
            ],
            actions=[
                {"type": RuleAction.ROUTE_TO.value, "agent": "perception_module"},
                {
                    "type": RuleAction.LOG.value,
                    "message": "Perception capability request routed",
                },
            ],
            enabled=True,
        )

        # Priority-based routing rules
        priority_rule = RoutingRule(
            rule_id="priority_critical",
            name="Critical Priority Routing",
            description="Route high priority requests",
            rule_type=RuleType.PRIORITY_BASED,
            priority=RulePriority.HIGHEST,
            conditions=[
                {"field": "priority", "operator": "equals", "value": "critical"}
            ],
            actions=[
                {"type": RuleAction.ROUTE_TO.value, "agent": "critical_handler"},
                {
                    "type": RuleAction.LOG.value,
                    "message": "Critical priority request routed",
                },
            ],
            enabled=True,
        )

        # Add rules
        self.add_rule(content_rule)
        self.add_rule(capability_rule)
        self.add_rule(priority_rule)


class RuleEngine:
    """Engine for managing multiple routing rule sets."""

    def __init__(self):
        """Initialize the rule engine."""
        self.engines: Dict[str, RoutingEngine] = {}
        self.default_engine = RoutingEngine()

    def get_engine(self, name: str = "default") -> RoutingEngine:
        """Get a routing engine."""
        return self.engines.get(name, self.default_engine)

    def create_engine(
        self, name: str, service_discovery: ServiceDiscovery = None
    ) -> RoutingEngine:
        """Create a new routing engine."""
        engine = RoutingEngine(service_discovery)
        self.engines[name] = engine
        return engine

    def remove_engine(self, name: str) -> bool:
        """Remove a routing engine."""
        if name in self.engines:
            del self.engines[name]
            return True
        return False

    def get_all_engines(self) -> Dict[str, RoutingEngine]:
        """Get all routing engines."""
        return self.engines.copy()

    def route_request(
        self,
        request_data: Dict[str, Any],
        engine_name: str = "default",
        context: Dict[str, Any] = None,
    ) -> RoutingResult:
        """Route a request using a specific engine."""
        engine = self.get_engine(engine_name)
        return engine.route_request(request_data, context)
