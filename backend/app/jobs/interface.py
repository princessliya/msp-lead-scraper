from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class JobHandle:
    job_id: int
    backend_id: str | None = None


class JobRunner(ABC):
    @abstractmethod
    def submit(self, func: Callable, *args: Any, job_id: int, **kwargs: Any) -> JobHandle: ...

    @abstractmethod
    def cancel(self, handle: JobHandle) -> bool: ...
