import logging
from typing import Any, Dict, List

from backend.agents.specialists.move_generator import WeeklyMove

logger = logging.getLogger("raptorflow.core.formatter")


class ActionPacketFormatter:
    """
    Industrial-grade Action Packet Formatter.
    Transforms weekly moves into surgically precise execution units.
    """

    @staticmethod
    def format_packet(move: WeeklyMove) -> List[Dict[str, Any]]:
        """
        Converts a WeeklyMove into a list of granular Action Packets.
        Format: {task, context, tool, owner, expected_outcome}
        """
        packets = []
        for item in move.action_items:
            packet = {
                "task": item.task,
                "owner": item.owner,
                "tools": item.tool_requirements,
                "context": move.description,
                "expected_outcome": move.desired_outcome,
                "industrial_id": f"MOVE-W{move.week_number}-{hash(item.task) % 10000}",
            }
            packets.append(packet)

        logger.info(f"Formatted {len(packets)} action packets for Move: {move.title}")
        return packets

    @staticmethod
    def to_markdown(packets: List[Dict[str, Any]]) -> str:
        """Generates a SOTA executive summary of action packets."""
        md = "### ⚡ INDUSTRIAL ACTION PACKET ###\n\n"
        for p in packets:
            md += f"**[{p['industrial_id']}] {p['task']}**\n"
            md += f"- **Owner:** {p['owner']}\n"
            md += f"- **Tools:** {', '.join(p['tools'])}\n"
            md += f"- **Goal:** {p['expected_outcome']}\n\n"
        return md
