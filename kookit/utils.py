from __future__ import annotations
import contextlib
from collections.abc import AsyncIterator
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Protocol

from fastapi import FastAPI


class ILifespan(Protocol):
    def __call__(self, app: FastAPI) -> AbstractAsyncContextManager[None]: ...


class Lifespans:
    def __init__(
        self,
        *lifespans: ILifespan,
    ) -> None:
        self.lifespans: list = list(lifespans)

    def add(self, *lifespans: ILifespan) -> None:
        self.lifespans.extend(lifespans)

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[None]:
        exit_stack = contextlib.AsyncExitStack()
        async with exit_stack:
            for lifespan in self.lifespans:
                await exit_stack.enter_async_context(lifespan(app))
            yield
