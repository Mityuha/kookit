from __future__ import annotations
import os
import queue
from contextlib import suppress
from itertools import cycle
from typing import Any, Final, Iterable

from fastapi import APIRouter
from multiprocess import Process
from pytest_mock import MockerFixture

from kookit.logging import logger
from kookit.utils import ILifespan
from .models import KookitHTTPRequest, KookitHTTPResponse
from .server import KookitHTTPServer
from .service import KookitHTTPService


__all__ = ["HTTPKookit"]


class HTTPKookit:
    server_port: Final[cycle] = cycle(i for i in range(29000, 30000))

    def __init__(self, mocker: MockerFixture) -> None:
        self.mocker: Final[MockerFixture] = mocker
        self.server: Final[KookitHTTPServer] = KookitHTTPServer(next(self.server_port))
        self.services: Final[list[KookitHTTPService]] = []
        self.server_process: Process | None = None

    def __str__(self) -> str:
        return "[HTTPKookit]"

    def new_service(
        self,
        env_var: str,
        *,
        unique_url: bool,
        actions: Iterable[KookitHTTPRequest | KookitHTTPResponse] = (),
        routers: Iterable[APIRouter] = (),
        lifespans: Iterable[ILifespan] = (),
        name: str = "",
    ) -> KookitHTTPService:
        server = self.server
        if unique_url:
            server = KookitHTTPServer(
                next(self.server_port),
            )

        if env_var:
            self.mocker.patch.dict(os.environ, {env_var: server.url})
        service = KookitHTTPService(
            server=server,
            actions=actions,
            routers=routers,
            lifespans=lifespans,
            unique_url=unique_url,
            name=name,
        )
        self.services.append(service)
        return service

    def __enter__(self) -> "HTTPKookit":
        not_unique = []
        for service in self.services:
            service.__enter__()
            if not service.unique_url:
                not_unique.append(service)

        if not_unique and not self.server_process:
            self.server_process = Process(
                target=self.server.run,
                args=([s.router for s in not_unique], [s.lifespan for s in not_unique]),
            )
            self.server_process.start()

            with suppress(queue.Empty):
                is_started = self.server.wait()
                if not is_started:
                    raise ValueError(f"{self}: bad value received from server while starting")

        return self

    def __exit__(self, *args: Any) -> None:
        if self.server_process:
            logger.trace(f"{self}: stop server process ({self.server.url})")
            self.server_process.terminate()
            self.server_process = None

            with suppress(queue.Empty):
                is_started: bool = self.server.wait()
                if is_started:
                    raise ValueError(f"{self}: bad value received from server while stopping")
        else:
            logger.trace(f"{self}: server process already stopped")

        for service in self.services:
            service.__exit__(*args)
