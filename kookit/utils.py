from __future__ import annotations
import contextlib
import json
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from traceback import extract_stack
from typing import TYPE_CHECKING, Any, Protocol
from uuid import UUID


if TYPE_CHECKING:
    from collections.abc import AsyncIterator


class ILifespan(Protocol):
    def __call__(self, app: Any) -> AbstractAsyncContextManager[None]: ...


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
