import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional, Sequence, Union

from core.base_tool import BaseRaptorTool
from skills.matrix_skills import (
    MatrixSkill,
    SkillPrivilegeMatrix,
    ToolExecutionWrapper,
    UserRole,
)

logger = logging.getLogger("raptorflow.tools.registry")


class ToolKind(str, Enum):
    TOOL = "tool"
    SKILL = "skill"


@dataclass(frozen=True)
class CapabilityDescriptor:
    cost: str
    latency_ms: int
    reliability: float
    permissions: Sequence[str]


@dataclass(frozen=True)
class CapabilityProfile:
    name: str
    description: str
    kind: ToolKind
    cost: str
    latency_ms: int
    reliability: float
    permissions: Sequence[str]


@dataclass
class RegistryEntry:
    name: str
    description: str
    kind: ToolKind
    implementation: Union[BaseRaptorTool, MatrixSkill]
    descriptor: CapabilityDescriptor


class SkillToolAdapter:
    """
    Adapter that exposes Matrix skills with a BaseRaptorTool-like run interface.
    """

    def __init__(self, skill: MatrixSkill, description: str):
        self._skill = skill
        self._description = description
        self._wrapper = ToolExecutionWrapper(skill)

    @property
    def name(self) -> str:
        return self._skill.name

    @property
    def description(self) -> str:
        return self._description

    async def run(self, **kwargs):
        return await self._wrapper.execute(kwargs)


class UnifiedToolRegistry:
    """
    Unified registry for BaseRaptorTool tools and Matrix skills with capability metadata.
    """

    _default_instance: Optional["UnifiedToolRegistry"] = None

    def __init__(self, rbac: Optional[SkillPrivilegeMatrix] = None):
        self._rbac = rbac or SkillPrivilegeMatrix()
        self._entries: Dict[str, RegistryEntry] = {}

    @classmethod
    def get_instance(cls) -> "UnifiedToolRegistry":
        """Get singleton instance of the registry."""
        return cls.default()

    @classmethod
    def default(cls) -> "UnifiedToolRegistry":
        if cls._default_instance is None:
            registry = cls()
            registry._register_default_tools()
            cls._default_instance = registry
        return cls._default_instance

    def _register_default_tools(self) -> None:
        # Register only essential tools that don't require additional config
        from tools.blackbox_roi import BlackboxROIHistoryTool
        from tools.conversion_optimization import ConversionOptimizationTool
        from tools.radar_trend_analyzer import RadarTrendAnalyzerTool
        from tools.search import RaptorSearchTool
        from tools.tavily import TavilyMultiHopTool

        self.register_tool(
            RaptorSearchTool(),
            CapabilityDescriptor(
                cost="low",
                latency_ms=800,
                reliability=0.9,
                permissions=self._all_role_permissions(),
            ),
        )
        self.register_tool(
            TavilyMultiHopTool(),
            CapabilityDescriptor(
                cost="medium",
                latency_ms=1200,
                reliability=0.92,
                permissions=self._all_role_permissions(),
            ),
        )
        self.register_tool(
            ConversionOptimizationTool(),
            CapabilityDescriptor(
                cost="low",
                latency_ms=500,
                reliability=0.95,
                permissions=self._all_role_permissions(),
            ),
        )
        self.register_tool(
            BlackboxROIHistoryTool(),
            CapabilityDescriptor(
                cost="low",
                latency_ms=400,
                reliability=0.98,
                permissions=self._all_role_permissions(),
            ),
        )
        self.register_tool(
            RadarTrendAnalyzerTool(),
            CapabilityDescriptor(
                cost="medium",
                latency_ms=700,
                reliability=0.9,
                permissions=self._all_role_permissions(),
            ),
        )

    def list_tools(self) -> List[RegistryEntry]:
        """List all registered tools."""
        return list(self._entries.values())

    def register_tool(
        self, tool: BaseRaptorTool, descriptor: CapabilityDescriptor
    ) -> None:
        logger.info("Registering tool %s", tool.name)
        self._entries[tool.name] = RegistryEntry(
            name=tool.name,
            description=tool.description,
            kind=ToolKind.TOOL,
            implementation=tool,
            descriptor=descriptor,
        )

    def register_skill(
        self,
        skill: MatrixSkill,
        descriptor: Optional[CapabilityDescriptor] = None,
        description: Optional[str] = None,
    ) -> None:
        logger.info("Registering matrix skill %s", skill.name)
        permissions = (
            descriptor.permissions
            if descriptor
            else self._skill_permissions(skill.name)
        )
        descriptor = descriptor or CapabilityDescriptor(
            cost="low",
            latency_ms=500,
            reliability=0.95,
            permissions=permissions,
        )
        skill_description = description or (skill.__doc__ or "Matrix skill")
        self._entries[skill.name] = RegistryEntry(
            name=skill.name,
            description=skill_description.strip(),
            kind=ToolKind.SKILL,
            implementation=skill,
            descriptor=descriptor,
        )

    def get_capability_profile(
        self, name: str, role: Optional[UserRole] = None
    ) -> Optional[CapabilityProfile]:
        entry = self._entries.get(name)
        if not entry:
            return None
        if entry.kind == ToolKind.SKILL and role is not None:
            self._enforce_rbac(role, entry.name)
        return CapabilityProfile(
            name=entry.name,
            description=entry.description,
            kind=entry.kind,
            cost=entry.descriptor.cost,
            latency_ms=entry.descriptor.latency_ms,
            reliability=entry.descriptor.reliability,
            permissions=entry.descriptor.permissions,
        )

    def get_capability_profiles(
        self, names: Iterable[str], role: Optional[UserRole] = None
    ) -> List[CapabilityProfile]:
        profiles = []
        for name in names:
            profile = self.get_capability_profile(name, role=role)
            if profile:
                profiles.append(profile)
        return profiles

    def list_capability_profiles(
        self, role: Optional[UserRole] = None
    ) -> List[CapabilityProfile]:
        profiles = []
        for name in self._entries:
            profile = self.get_capability_profile(name, role=role)
            if profile:
                profiles.append(profile)
        return profiles

    def resolve_tools_from_profiles(
        self, profiles: Sequence[CapabilityProfile], role: Optional[UserRole] = None
    ) -> List[Union[BaseRaptorTool, SkillToolAdapter]]:
        tools: List[Union[BaseRaptorTool, SkillToolAdapter]] = []
        for profile in profiles:
            entry = self._entries.get(profile.name)
            if not entry:
                continue
            if entry.kind == ToolKind.SKILL and role is not None:
                self._enforce_rbac(role, entry.name)
            if entry.kind == ToolKind.SKILL:
                tools.append(SkillToolAdapter(entry.implementation, entry.description))
            else:
                tools.append(entry.implementation)
        return tools

    def _enforce_rbac(self, role: UserRole, skill_name: str) -> None:
        if not self._rbac.has_permission(role, skill_name):
            raise PermissionError(
                f"Role '{role.value}' does not have access to skill '{skill_name}'."
            )

    def _skill_permissions(self, skill_name: str) -> List[str]:
        return [
            role.value
            for role in UserRole
            if self._rbac.has_permission(role, skill_name)
        ]

    @staticmethod
    def _all_role_permissions() -> List[str]:
        return [role.value for role in UserRole]
