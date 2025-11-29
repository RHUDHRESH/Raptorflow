
from __future__ import annotations
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from datetime import datetime

class ThoughtType(str, Enum):
    ANALYSIS = "analysis"
    HYPOTHESIS = "hypothesis"
    PLAN = "plan"
    CRITIQUE = "critique"
    REFINEMENT = "refinement"
    DECISION = "decision"

class ThoughtScore(BaseModel):
    value: float = Field(..., ge=0.0, le=1.0, description="Score of the thought")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the score")
    reasoning: str = Field(..., description="Reasoning behind the score")

class ThoughtNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    parent_id: Optional[str] = None
    thought_type: ThoughtType
    content: str
    score: Optional[ThoughtScore] = None
    children: List[ThoughtNode] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def add_child(self, node: ThoughtNode):
        self.children.append(node)

class ThoughtTree(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    root_id: str
    nodes: Dict[str, ThoughtNode] = Field(default_factory=dict)
    objective: str
    context: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    def add_node(self, node: ThoughtNode):
        self.nodes[node.id] = node
        if node.parent_id and node.parent_id in self.nodes:
            self.nodes[node.parent_id].add_child(node)

    def get_node(self, node_id: str) -> Optional[ThoughtNode]:
        return self.nodes.get(node_id)
    
    def get_root(self) -> Optional[ThoughtNode]:
        return self.nodes.get(self.root_id)
