from dataclasses import dataclass, field


@dataclass
class QueryPlan:
    intent: str
    entity: str | None = None
    filters: dict[str, str] = field(default_factory=dict)
    output: str = "list"