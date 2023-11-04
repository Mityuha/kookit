from typing import Final, Iterable

import uvicorn
from fastapi import FastAPI

from .interfaces import IKookitService


class KookitServer:
    def __init__(self, *, host: str = "127.0.0.1", port: int = 20000) -> None:
        self.host: Final[str] = host
        self.port: Final[int] = port
        self.url: Final[str] = f"http://{host}:{port}"

    async def run(self, services: Iterable[IKookitService]) -> None:
        app: FastAPI = FastAPI()
        for service in services:
            app.include_router(service.router)

        uvicorn.run(app, host=self.host, port=self.port)
