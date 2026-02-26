from __future__ import annotations

import logging
import threading
from typing import Any, Callable

from app.jobs.interface import JobHandle, JobRunner

log = logging.getLogger(__name__)


class BackgroundJobRunner(JobRunner):
    """Runs jobs in background daemon threads."""

    def __init__(self):
        self._threads: dict[int, threading.Thread] = {}

    def submit(self, func: Callable, *args: Any, job_id: int, **kwargs: Any) -> JobHandle:
        def wrapper():
            try:
                func(*args, **kwargs)
            except Exception as e:
                log.error(f"Background job {job_id} failed: {e}")
            finally:
                self._threads.pop(job_id, None)

        thread = threading.Thread(target=wrapper, daemon=True, name=f"scrape-job-{job_id}")
        self._threads[job_id] = thread
        thread.start()
        return JobHandle(job_id=job_id)

    def cancel(self, handle: JobHandle) -> bool:
        return handle.job_id in self._threads

    def is_running(self, job_id: int) -> bool:
        return job_id in self._threads
