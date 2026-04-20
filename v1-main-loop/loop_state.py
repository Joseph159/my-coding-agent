from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class Transition(Enum):
    TOOL_RESULT = "tool_result"


@dataclass
class LoopState:
    messages: list[dict[str, Any]] = field(default_factory=list)
    turn: int = 0
    transition: Optional[Transition] = None
