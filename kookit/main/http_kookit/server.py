from contextlib import asynccontextmanager
from typing import AsyncIterator, Final, Iterable

import uvicorn
from fastapi import FastAPI
from multiprocess import Queue

from .interfaces import IKookitHTTPService


class KookitHTTPServer:
    def __init__(self, queue: Queue, *, host: str = "127.0.0.1", port: int = 20000) -> None:
        self.queue: Final[Queue] = queue
        self.host: Final[str] = host
        self.port: Final[int] = port
        self.url: Final[str] = f"http://{host}:{port}"

    def run(self, services: Iterable[IKookitHTTPService]) -> None:
        @asynccontextmanager
        async def notify_lifespan(app: FastAPI) -> AsyncIterator:
            self.queue.put(True)
            yield
            self.queue.put(False)

        app: FastAPI = FastAPI(lifespan=notify_lifespan)
        for service in services:
            app.include_router(service.router)

        uvicorn.run(app, host=self.host, port=self.port)
