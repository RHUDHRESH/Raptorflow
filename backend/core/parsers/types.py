from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class ParsedAsset:
    text: str
    title: str
    metadata: Dict[str, Any] = field(default_factory=dict)
