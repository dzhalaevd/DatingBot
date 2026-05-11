import dataclasses
import time


@dataclasses.dataclass(eq=False)
class CancelHandler(Exception):
    title: str | None = None


@dataclasses.dataclass(eq=False)
class Throttled(Exception):
    title: str | None = None
    key: str = '<None>'
    called_at: float = dataclasses.field(default_factory=time.time)
    rate: float | None = None
    exceeded_count: int = 0
    delta: float = 0.0
    user: int | None = None
    chat: int | None = None

    def __str__(self) -> str:
        return f"Rate limit exceeded! (Limit: {self.rate} s, " \
               f"exceeded: {self.exceeded_count}, " \
               f"time delta: {round(self.delta, 3)} s)"
