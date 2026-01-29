"""
Document Stitcher for aggregating multi-page OCR results.
"""

import logging
from typing import List
from ..base import OCRResponse

logger = logging.getLogger(__name__)


class DocumentStitcher:
    """
    Stitches multiple OCR results from separate pages into a single response.
    """

    async def stitch(self, responses: List[OCRResponse]) -> OCRResponse:
        """
        Aggregate a list of OCRResponse objects into one.

        Args:
            responses: List of responses, one per page.

        Returns:
            A single aggregated OCRResponse.
        """
        if not responses:
            raise ValueError("Cannot stitch empty list of responses")

        # Sort by page metadata if available, otherwise assume order
        sorted_responses = sorted(
            responses, key=lambda r: r.metadata.get("page_number", 0)
        )

        stitched_text = (
            "\n\n---"
            + " Page Break "
            + "---"
            + "\n\n".join([r.text for r in sorted_responses])
        )
        total_pages = sum([r.pages for r in responses])

        # Combine tables and raw data
        all_tables = []
        for r in responses:
            all_tables.extend(r.tables)

        # Use metadata from first page as base
        base_metadata = responses[0].metadata.copy()
        base_metadata["stitched"] = True
        base_metadata["original_page_count"] = len(responses)

        return OCRResponse(
            text=stitched_text,
            raw_data={"individual_responses": [r.raw_data for r in responses]},
            metadata=base_metadata,
            confidence=sum([r.confidence for r in responses]) / len(responses),
            pages=total_pages,
            tables=all_tables,
        )
