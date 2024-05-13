from __future__ import annotations
import os
import queue
import time
from contextlib import suppress
from itertools import cycle
from typing import TYPE_CHECKING, Final, Iterable

from multiprocess import Process
from typing_extensions import Self

from kookit.logging import logger
from .server import KookitHTTPServer
from .service import KookitHTTPService


if TYPE_CHECKING:
    from types import TracebackType

    from fastapi import APIRouter
    from pytest_mock import MockerFixture

    from kookit.utils import ILifespan
    from .models import KookitHTTPRequest, KookitHTTPResponse


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

    def __enter__(self) -> Self:
        # 1. start global server
        # 2. start all other services' servers.
        not_unique = [s for s in self.services if not s.unique_url]

        if not_unique and not self.server_process:
            self.server_process = Process(
                target=self.server.run,
                args=(
                    [s.router for s in not_unique],
                    [s.lifespan for s in not_unique],
                ),
            )
            self.server_process.start()
            time.sleep(0.01)

            with suppress(queue.Empty):
                is_started = self.server.wait()
                if not is_started:
                    msg = f"{self}: bad value received from server while starting"
                    raise ValueError(msg)

        for service in self.services:
            service.__enter__()

        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        # 1. stop global service
        # 2. stop all other services' servers
        if self.server_process:
            logger.trace(f"{self}: stop server process ({self.server.url})")
            self.server_process.terminate()
            time.sleep(0.01)

            self.server_process = None

            with suppress(queue.Empty):
                is_started: bool = self.server.wait()
                if is_started:
                    msg = f"{self}: bad value received from server while stopping"
                    raise ValueError(msg)
        else:
            logger.trace(f"{self}: server process already stopped")

        for service in self.services:
            service.__exit__(typ, exc, tb)
