from dataclasses import dataclass
from typing import Any


@dataclass
class ExecuteResponse:
    succeeded: bool
    message: str
    value: Any | None = None
    exception: Exception | None = None
