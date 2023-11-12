import os
from typing import Any, AsyncIterator, Final, Iterable, List, Mapping, Optional

import anyio
from pytest import fixture
from pytest_mock import MockerFixture

from ..logging import logger
from .client_side import KookitHTTPAsyncClient
from .http_kookit import HTTPKookit
from .interfaces import IKookit


class Kookit(KookitHTTPAsyncClient):
    def __init__(self, mocker: MockerFixture) -> None:
        self.mocker: Final[MockerFixture] = mocker
        self.kookits: Final[List[IKookit]] = [HTTPKookit(mocker)]
        super().__init__()

    def __str__(self) -> str:
        return "[kookit]"

    async def prepare_services(self, *services: Any) -> None:
        logger.trace(f"{self}: preparing {len(services)} services: {services}")
        unfit_services: Iterable[Any] = services
        for kookit in self.kookits:
            unfit_services = await kookit.prepare_services(*unfit_services)

        assert not unfit_services, f"Unknown services: {unfit_services}"

    async def start_services(
        self,
        http_wait_for_server_launch: Optional[float] = None,
    ) -> None:
        logger.trace(f"{self}: starting services")
        for kookit in self.kookits:
            await kookit.start_services(
                http_wait_for_server_launch=http_wait_for_server_launch,
            )

    async def stop_services(
        self,
        http_wait_for_server_stop: Optional[float] = 0.0,
    ) -> None:
        logger.trace(f"{self}: stopping services")
        for kookit in self.kookits:
            await kookit.stop_services(
                http_wait_for_server_stop=http_wait_for_server_stop,
            )

    async def __aenter__(self) -> "Kookit":
        return self

    async def __aexit__(self, *_args: Any) -> None:
        await self.stop_services()

    async def wait(self, seconds: float) -> None:
        await anyio.sleep(seconds)

    async def patch_env(self, new_env: Mapping[str, str]) -> None:
        self.mocker.patch.dict(os.environ, new_env)


@fixture
async def kookit(mocker: MockerFixture) -> AsyncIterator[Kookit]:
    async with Kookit(mocker) as kooky:
        yield kooky
