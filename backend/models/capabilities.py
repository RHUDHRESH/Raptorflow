from typing import List, Optional

from pydantic import BaseModel, Field

from skills.matrix_skills import SkillPrivilegeMatrix, UserRole


class CapabilityProfile(BaseModel):
    """Defines which tools and skills an agent is allowed to use."""

    name: str
    allowed_tools: Optional[List[str]] = Field(default=None)
    allowed_skills: Optional[List[str]] = Field(default=None)
    rbac_role: Optional[UserRole] = Field(default=None)

    def allows_tool(self, tool_name: str) -> bool:
        if self.allowed_tools is None:
            return True
        return tool_name in self.allowed_tools

    def allows_skill(
        self, skill_name: str, rbac_matrix: Optional[SkillPrivilegeMatrix] = None
    ) -> bool:
        if self.allowed_skills is not None and skill_name not in self.allowed_skills:
            return False

        if self.rbac_role and rbac_matrix:
            return rbac_matrix.has_permission(self.rbac_role, skill_name)

        return True
