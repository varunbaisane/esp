from dataclasses import dataclass, field
from typing import Optional

@dataclass
class EmailMessage:
    subject: str
    to: list[str] = field(default_factory=list)
    cc: list[str] = field(default_factory=list)
    bcc: list[str] = field(default_factory=list)
    text: Optional[str] = None
    html: Optional[str] = None
