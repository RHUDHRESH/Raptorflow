## OCR Complex — No-Excuses Document Processing

Explicit success/failure OCR + NLP stack with Gemini/Tesseract, parsers, PII, QA, API, CLI.

### Features
- OCR: Tesseract/Gemini hybrid, multi-language, handwriting, preprocessing (deskew/denoise/contrast/binarize), Gemini vision.
- Documents: PDF tables/layout, CSV/Excel/JSON/XML parsers.
- Special: barcode/QR, receipts/invoices, business cards, form KV, multi-lang OCR.
- NLP: sentiment, entities, summary, topics, keywords, language detection, classification, QA.
- Privacy/Similarity: PII detect/mask, similarity/dedup.
- Infra: caching, batch queue, logging, FastAPI, CLI, benchmarks, integration tests.

### Install
```bash
pip install -r requirements.txt
# ensure system deps: tesseract-ocr, poppler (for pdf2image), zbar (for pyzbar)
```

### Programmatic usage
```python
from ocr_complex.ocr_complex import OCRComplex

ocr = OCRComplex({
    "gemini_api_key": "YOUR_KEY",   # optional for AI path
    "log_path": "logs/ocr.log"
})

result = ocr.process_document("sample.pdf", options={
    "nlp": True,
    "nlp_tasks": ["sentiment","entities","summary"],
    "translate_to": "es"
})
if not result["success"]:
    raise RuntimeError(result["error"])
print(result["final_output"]["extracted_content"]["text"])
```

### CLI
```bash
python -m ocr_complex.cli process --file sample.pdf --translate-to es
python -m ocr_complex.cli batch --files a.pdf b.png
```

### FastAPI
```bash
uvicorn ocr_complex.api:app --host 0.0.0.0 --port 8000
# POST /process (file upload), POST /batch, GET /health
```

### Tests & Benchmarks
```bash
python -m ocr_complex.integration_tests   # synthetic integration tests
python -m ocr_complex.benchmarks          # simple perf smoke
```

### Key modules
- `ocr_engine.py` / `ocr_multilang.py` / `vision_gemini.py`: OCR engines.
- `preprocess.py`: image preprocessing.
- `pdf_tools.py`: PDF tables/layout.
- `data_parsers.py`: CSV/Excel/JSON/XML.
- `special_parsers.py`: barcode/QR, receipts, business cards, forms, handwriting.
- `nlp_engine.py` / `nlp_extra.py`: NLP tasks and extras.
- `privacy_similarity.py`: PII redaction, similarity/dedup.
- `qa_module.py`: document QA.
- `caching.py`, `queue_system.py`, `logging_utils.py`: infra.
- `api.py`, `cli.py`, `benchmarks.py`, `integration_tests.py`.

### Configuration knobs (examples)
```python
config = {
  "gemini_api_key": "...",
  "google_translate_api_key": "...",
  "auto_nlp": True,
  "gemini_threshold": 0.7,
  "cache_dir": ".ocr_cache",
  "log_path": "logs/ocr.log",
}
```

### Failure semantics
- Every operation returns explicit success/failure plus error reason.
- Verification steps enforce confidence/integrity; no silent/“graceful” failure paths.
