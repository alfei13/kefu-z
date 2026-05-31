from dataclasses import dataclass, field


@dataclass
class HandoffRequest:
    target_agent: str
    reason: str
    context: dict = field(default_factory=dict)
    original_message: str = ""
