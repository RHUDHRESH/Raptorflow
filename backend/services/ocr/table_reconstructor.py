"""
Table Reconstructor for mapping OCR blocks into structured tabular data.
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TableReconstructor:
    """
    Reconstructs tables from OCR text blocks based on spatial coordinates.
    """

    def __init__(self):
        pass

    async def reconstruct(self, blocks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert raw OCR blocks with bounds into a structured list of dictionaries.
        
        Args:
            blocks: List of dicts containing 'text' and 'bounds' (spatial data).
            
        Returns:
            List of dictionaries representing the table rows.
        """
        if not blocks:
            return []

        # Sort blocks by Y coordinate (rows) then X (columns)
        # Bounds format: [ymin, xmin, ymax, xmax]
        sorted_blocks = sorted(blocks, key=lambda b: (b["bounds"][0], b["bounds"][1]))
        
        # Simple row grouping logic: if y-difference is small, it's the same row
        rows = []
        if not sorted_blocks:
            return []
            
        current_row = [sorted_blocks[0]]
        for i in range(1, len(sorted_blocks)):
            prev_block = sorted_blocks[i-1]
            curr_block = sorted_blocks[i]
            
            # If vertical centers are close enough, group as row
            if abs(curr_block["bounds"][0] - prev_block["bounds"][0]) < 5:
                current_row.append(curr_block)
            else:
                rows.append(current_row)
                current_row = [curr_block]
        rows.append(current_row)
        
        if not rows:
            return []
            
        # Use first row as headers
        headers = [block["text"] for block in rows[0]]
        
        table_data = []
        for row_blocks in rows:
            row_dict = {}
            # Map each block in row to header based on horizontal position
            # For simplicity in this initial version, we use index alignment
            for i, header in enumerate(headers):
                if i < len(row_blocks):
                    row_dict[header] = row_blocks[i]["text"]
                else:
                    row_dict[header] = ""
            table_data.append(row_dict)
            
        return table_data
