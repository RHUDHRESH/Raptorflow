"""
DATA PARSERS
CSV/Excel/JSON/XML parsing with schema detection.
Explicit success/failure with reasons.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd
import xmltodict

from ...base_processor import BaseProcessor, ProcessingResult, ProcessingStatus


class CSVParser(BaseProcessor):
    """Parse CSV files with delimiter detection."""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        try:
            encoding = self._detect_encoding(path)
            with open(path, "r", encoding=encoding) as file:
                sample = file.read(2048)
                file.seek(0)
                delimiter = csv.Sniffer().sniff(sample).delimiter
                reader = csv.DictReader(file, delimiter=delimiter)
                rows = list(reader)
                if not rows:
                    return ProcessingResult(
                        status=ProcessingStatus.FAILURE,
                        error="CSV empty or invalid",
                        verified=False,
                    )
                data = {
                    "content": self._rows_to_text(rows),
                    "structured_data": rows,
                    "headers": reader.fieldnames,
                    "row_count": len(rows),
                    "column_count": len(reader.fieldnames) if reader.fieldnames else 0,
                    "delimiter": delimiter,
                    "encoding": encoding,
                }
                return ProcessingResult(
                    status=ProcessingStatus.SUCCESS,
                    data=data,
                    confidence=1.0,
                    verified=False,
                )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"CSV parsing failed: {str(e)}",
                verified=False,
            )

    def _detect_encoding(self, path: Path) -> str:
        encodings = ["utf-8", "utf-16", "latin-1", "cp1252"]
        for enc in encodings:
            try:
                with open(path, "r", encoding=enc) as f:
                    f.read()
                return enc
            except UnicodeDecodeError:
                continue
        return "utf-8"

    def _rows_to_text(self, rows: List[Dict]) -> str:
        lines = []
        for row in rows:
            line = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
            if line:
                lines.append(line)
        return "\n".join(lines)


class ExcelParser(BaseProcessor):
    """Parse Excel files with schema detection."""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        try:
            sheets = pd.read_excel(path, sheet_name=None, dtype=str)
            if not sheets:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="Excel file has no sheets",
                    verified=False,
                )
            parsed_sheets = []
            for name, df in sheets.items():
                df = df.dropna(how="all")
                if df.empty:
                    continue
                parsed_sheets.append(
                    {
                        "sheet": name,
                        "rows": int(df.shape[0]),
                        "cols": int(df.shape[1]),
                        "headers": df.columns.tolist(),
                        "preview": df.head(5).fillna("").to_dict(orient="records"),
                        "csv": df.to_csv(index=False),
                    }
                )
            if not parsed_sheets:
                return ProcessingResult(
                    status=ProcessingStatus.FAILURE,
                    error="Excel sheets are empty",
                    verified=False,
                )
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={"sheets": parsed_sheets, "sheet_count": len(parsed_sheets)},
                confidence=1.0,
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"Excel parsing failed: {str(e)}",
                verified=False,
            )


class JSONParser(BaseProcessor):
    """Parse JSON files."""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "content": json.dumps(data, indent=2),
                    "structured_data": data,
                    "top_level_keys": (
                        list(data.keys()) if isinstance(data, dict) else []
                    ),
                },
                confidence=1.0,
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"JSON parsing failed: {str(e)}",
                verified=False,
            )


class XMLParser(BaseProcessor):
    """Parse XML files into dict representation."""

    def _process_document(self, document_path: Union[str, Path]) -> ProcessingResult:
        path = Path(document_path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                xml_text = f.read()
            parsed = xmltodict.parse(xml_text)
            return ProcessingResult(
                status=ProcessingStatus.SUCCESS,
                data={
                    "content": json.dumps(parsed, indent=2),
                    "structured_data": parsed,
                    "root_keys": (
                        list(parsed.keys()) if isinstance(parsed, dict) else []
                    ),
                },
                confidence=0.9,
                verified=False,
            )
        except Exception as e:
            return ProcessingResult(
                status=ProcessingStatus.FAILURE,
                error=f"XML parsing failed: {str(e)}",
                verified=False,
            )
