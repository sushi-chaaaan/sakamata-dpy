from dataclasses import dataclass
from typing import Any


@dataclass
class ExecuteResponse:
    succeeded: bool
    exception: Exception | None
    message: str
    value: Any
