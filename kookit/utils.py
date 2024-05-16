from __future__ import annotations
import contextlib
import json
import sys
import time
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from traceback import extract_stack
from typing import TYPE_CHECKING, Any, Callable, Final
from uuid import UUID

from kookit.logging import logger


if TYPE_CHECKING:
    from collections.abc import AsyncIterator
    from types import TracebackType

    from multiprocess import Process
    from typing_extensions import Self

if sys.version_info >= (3, 9):
    ILifespan = Callable[[Any], AbstractAsyncContextManager[None]]
else:
    ILifespan = Callable[[Any], AbstractAsyncContextManager]


class Lifespans:
    def __init__(
        self,
        *lifespans: ILifespan,
    ) -> None:
        self.lifespans: list = list(lifespans)

    def add(self, *lifespans: ILifespan) -> None:
        self.lifespans.extend(lifespans)

    @asynccontextmanager
    async def __call__(self, app: Any) -> AsyncIterator[None]:
        exit_stack = contextlib.AsyncExitStack()
        async with exit_stack:
            for lifespan in self.lifespans:
                await exit_stack.enter_async_context(lifespan(app))
            yield


def lvalue_from_assign(depth: int = 3) -> str:
    (_, _, _, text) = extract_stack()[-depth]
    pos = text.find("=")
    if pos == -1:
        return ""
    return text[:pos].strip()


class UUIDEncoder(json.JSONEncoder):
    def default(self, value: Any) -> str:
        if isinstance(value, UUID):
            return str(value)
        return super().default(value)


class ProcessManager:
    DEFAULT_STARTUP_TIMEOUT: Final = 3
    DEFAULT_SHUTDOWN_TIMEOUT: Final = 3

    def __init__(
        self,
        process: Process,
        *,
        startup_timeout: float,
        shutdown_timeout: float,
        parent: Any,
        wait_func: Callable[[float], bool],
    ) -> None:
        self.process: Final = process
        self.startup_timeout: Final = startup_timeout
        self.parent: Final = parent
        self.wait_func: Final = wait_func
        self.shutdown_timeout: Final = shutdown_timeout

    def __repr__(self) -> str:
        return self.parent

    def __enter__(self) -> Self:
        self.process.start()
        time.sleep(0.01)

        logger.trace(
            f"{self}: waiting for process to start ({self.startup_timeout} seconds)",
        )
        is_started: bool = self.wait_func(self.startup_timeout)

        if not is_started:
            logger.trace(
                f"{self}: process didn't respond for {self.startup_timeout} seconds. Stopping."
            )
            self.__exit__(None, None, None)
            msg = f"{self}: process was not started. Check logs."
            raise RuntimeError(msg)

        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        logger.trace(f"{self}: stopping server process")
        self.process.terminate()
        logger.trace(f"{self}: waiting for process to join ({self.shutdown_timeout} seconds)")
        self.process.join(self.shutdown_timeout)
        if self.process.exitcode is None:
            self.process.kill()
            self.process.join(self.shutdown_timeout)

        logger.trace(f"{self}: process joined ({self.process.exitcode})")
