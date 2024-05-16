from __future__ import annotations
import os
import sys
import time
from typing import TYPE_CHECKING, Final, Iterable, Mapping

import anyio
import pytest
from typing_extensions import Self

from .client_side import KookitHTTPClient
from .http_kookit import HTTPKookit, KookitHTTPRequest, KookitHTTPResponse
from .interfaces import IKookitHTTPService
from .logging import logger
from .utils import ILifespan, ProcessManager, lvalue_from_assign


if TYPE_CHECKING:
    from types import TracebackType

    from fastapi import APIRouter
    from pytest_mock import MockerFixture


__all__ = ["IKookitHTTPService", "Kookit", "kookit"]


class Kookit(KookitHTTPClient):
    def __init__(self, mocker: MockerFixture) -> None:
        self.mocker: Final[MockerFixture] = mocker
        self.http_kookit: Final = HTTPKookit(mocker)
        super().__init__()

    def __str__(self) -> str:
        return "[kookit]"

    def __call__(
        self,
        startup_timeout: float = ProcessManager.DEFAULT_STARTUP_TIMEOUT,
        *,
        shutdown_timeout: float = ProcessManager.DEFAULT_SHUTDOWN_TIMEOUT,
    ) -> Self:
        for kookit in [self.http_kookit]:
            kookit(
                startup_timeout=startup_timeout,
                shutdown_timeout=shutdown_timeout,
            )

        return self

    def __enter__(self) -> Self:
        logger.trace(f"{self}: starting services")
        for kookit in [self.http_kookit]:
            kookit.__enter__()
        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        logger.trace(f"{self}: stopping services")
        for kookit in [self.http_kookit]:
            kookit.__exit__(typ, exc, tb)

    async def __aenter__(self) -> Self:
        return self.__enter__()

    async def __aexit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return self.__exit__(typ, exc, tb)

    def new_http_service(
        self,
        env_var: str = "",
        *,
        unique_url: bool = False,
        actions: Iterable[KookitHTTPRequest | KookitHTTPResponse] = (),
        routers: Iterable[APIRouter] = (),
        lifespans: Iterable[ILifespan] = (),
        name: str = "",
    ) -> IKookitHTTPService:
        name = name or lvalue_from_assign()
        return self.http_kookit.new_service(
            env_var,
            unique_url=unique_url,
            actions=actions,
            routers=routers,
            lifespans=lifespans,
            name=name,
        )

    def sleep(self, seconds: float) -> None:
        return time.sleep(seconds)

    async def asleep(self, seconds: float) -> None:
        return await anyio.sleep(seconds)

    def patch_env(self, new_env: Mapping[str, str]) -> None:
        self.mocker.patch.dict(os.environ, new_env)

    @staticmethod
    def show_logs() -> None:
        logger.remove()
        logger.add(sys.stdout, level="TRACE")


@pytest.fixture()
def kookit(mocker: MockerFixture) -> Iterable[Kookit]:
    # ruff: noqa: PT022
    yield Kookit(mocker)
