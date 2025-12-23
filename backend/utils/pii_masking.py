import re
from typing import Any, Dict, List, Union

# Regex patterns for common PII
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_PATTERN = re.compile(r"\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}")

def mask_pii(data: Any) -> Any:
    """
    Recursively masks PII in strings, lists, and dictionaries.
    """
    if isinstance(data, str):
        # Mask emails
        masked = EMAIL_PATTERN.sub("[EMAIL_MASKED]", data)
        # Mask phone numbers
        masked = PHONE_PATTERN.sub("[PHONE_MASKED]", masked)
        return masked
    
    if isinstance(data, dict):
        return {k: mask_pii(v) for k, v in data.items()}
    
    if isinstance(data, list):
        return [mask_pii(item) for item in data]
    
    return data
