from __future__ import annotations
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Final, Iterable

import uvicorn
from fastapi import APIRouter, FastAPI
from multiprocess import Queue

from kookit.logging import logger
from kookit.utils import ILifespan, Lifespans


class KookitHTTPServer:
    def __init__(self, port: int, *, host: str = "127.0.0.1") -> None:
        self.queue: Final = Queue()
        self.host: Final[str] = host
        self.port: Final[int] = port
        self.url: Final[str] = f"http://{host}:{port}"

    def __str__(self) -> str:
        return "[KookitHTTPServer]"

    def wait(self, timeout: float | None = None) -> Any:
        return self.queue.get(timeout=timeout)

    def run(
        self,
        routers: Iterable[APIRouter],
        lifespans: Iterable[ILifespan],
    ) -> None:
        @asynccontextmanager
        # ruff: noqa: ARG001
        async def notify_lifespan(app: FastAPI) -> AsyncIterator:
            # ruff: noqa: FBT003
            self.queue.put(True)
            yield
            self.queue.put(False)

        @asynccontextmanager
        async def routers_lifespan(app: FastAPI) -> AsyncIterator:
            for router in routers:
                app.include_router(router)
            yield

        app: FastAPI = FastAPI(
            lifespan=Lifespans(
                *lifespans,
                routers_lifespan,
                notify_lifespan,
            ),
        )

        logger.trace(f"{self}: running uvicorn on port {self.port}")

        uvicorn.run(app, host=self.host, port=self.port)
