"""
PDF UTILITIES
Table extraction and basic layout analysis.
No graceful failures: explicit success/failure with reasons.
"""

import io
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
import pdfplumber

from ...base_processor import BaseProcessor, ProcessingResult, ProcessingStatus


class PDFTableExtractor(BaseProcessor):
    """Extracts tables from PDFs using pdfplumber."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_pages = config.get("max_pages", 10)
        self.max_tables = config.get("max_tables", 20)

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)

        try:
            tables = []
            with pdfplumber.open(path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    if page_idx >= self.max_pages:
                        break

                    page_tables = page.extract_tables()
                    for tbl in page_tables:
                        if len(tables) >= self.max_tables:
                            break
                        df = pd.DataFrame(tbl)
                        # Drop completely empty rows/cols
                        df = df.dropna(how="all", axis=0).dropna(how="all", axis=1)
                        if df.empty:
                            continue
                        tables.append(
                            {
                                "page": page_idx + 1,
                                "rows": df.shape[0],
                                "cols": df.shape[1],
                                "csv": df.to_csv(index=False),
                                "preview": df.head(5).to_dict(orient="records"),
                            }
                        )

            if not tables:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No tables detected",
                    verified=False,
                )

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "tables": tables,
                    "table_count": len(tables),
                },
                confidence=1.0,
                verified=False,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"PDF table extraction failed: {str(e)}",
                verified=False,
            )


class PDFLayoutAnalyzer(BaseProcessor):
    """Performs simple layout analysis: headings, paragraphs, images."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_pages = config.get("max_pages", 5)

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)

        try:
            layout = []
            with pdfplumber.open(path) as pdf:
                for page_idx, page in enumerate(pdf.pages):
                    if page_idx >= self.max_pages:
                        break

                    page_info = {"page": page_idx + 1, "headings": [], "paragraphs": []}
                    # Extract text with font sizes to guess headings
                    for obj in page.extract_words(extra_attrs=["size"]):
                        text = obj.get("text", "").strip()
                        size = obj.get("size", 0)
                        if not text:
                            continue
                        if size >= 14:  # heuristic for heading
                            page_info["headings"].append({"text": text, "size": size})
                    # Paragraph extraction
                    paragraphs = page.extract_text(layout=True)
                    if paragraphs:
                        page_info["paragraphs"] = [
                            p.strip() for p in paragraphs.split("\n\n") if p.strip()
                        ]
                    layout.append(page_info)

            if not layout:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="No layout information extracted",
                    verified=False,
                )

            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={"pages": layout, "page_count": len(layout)},
                confidence=0.8,
                verified=False,
            )

        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"PDF layout analysis failed: {str(e)}",
                verified=False,
            )
