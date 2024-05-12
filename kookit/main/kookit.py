from __future__ import annotations
import os
import time
from contextlib import AbstractAsyncContextManager
from typing import Any, Final, Iterable, Mapping

import anyio
from fastapi import APIRouter
from pytest import fixture
from pytest_mock import MockerFixture

from ..http_models import KookitHTTPRequest, KookitHTTPResponse
from ..logging import logger
from ..utils import lvalue_from_assign
from .client_side import KookitHTTPAsyncClient
from .http_kookit import HTTPKookit
from .interfaces import IKookitHTTPService


class Kookit(KookitHTTPAsyncClient):
    def __init__(self, mocker: MockerFixture) -> None:
        self.mocker: Final[MockerFixture] = mocker
        self.http_kookit: Final = HTTPKookit(mocker)
        super().__init__()

    def __str__(self) -> str:
        return "[kookit]"

    def start(self) -> None:
        logger.trace(f"{self}: starting services")
        for kookit in [self.http_kookit]:
            kookit.__enter__()

    def stop(self) -> None:
        logger.trace(f"{self}: stopping services")
        for kookit in [self.http_kookit]:
            kookit.__exit__(None, None, None)

    def __enter__(self) -> "Kookit":
        self.start()
        return self

    def __exit__(self, *_args: Any) -> None:
        self.stop()

    async def __aenter__(self) -> "Kookit":
        self.start()
        return self

    async def __aexit__(self, *_args: Any) -> None:
        self.stop()

    def new_http_service(
        self,
        env_var: str = "",
        *,
        unique_url: bool = False,
        actions: Iterable[KookitHTTPRequest | KookitHTTPResponse] = (),
        routers: Iterable[APIRouter] = (),
        lifespans: Iterable[AbstractAsyncContextManager] = (),
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

    def wait(self, seconds: float) -> Any:
        if anyio.get_running_loop():
            return anyio.sleep(seconds)
        return time.sleep(seconds)

    def patch_env(self, new_env: Mapping[str, str]) -> None:
        self.mocker.patch.dict(os.environ, new_env)


@fixture
def kookit(mocker: MockerFixture) -> Iterable[Kookit]:
    yield Kookit(mocker)
