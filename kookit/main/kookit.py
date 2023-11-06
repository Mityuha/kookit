import os
import queue
from contextlib import suppress
from itertools import cycle
from typing import Any, AsyncIterator, Final, List, Optional

import anyio
from multiprocess import Process, Queue
from pytest import fixture
from pytest_mock import MockerFixture

from ..logging import logger
from .client_side import KookitHTTPAsyncClient
from .interfaces import IKookitService
from .server import KookitServer


class Kookit(KookitHTTPAsyncClient):
    server_port: Final[cycle] = cycle(i for i in range(29000, 30000))

    def __init__(self, mocker: MockerFixture) -> None:
        self.mocker: Final[MockerFixture] = mocker
        self.server_queue: Final[Queue] = Queue()
        self.server: Final[KookitServer] = KookitServer(
            self.server_queue,
            port=next(self.server_port),
        )
        self.services: Final[List[IKookitService]] = []
        self.server_process: Optional[Process] = None
        super().__init__()

    def __str__(self) -> str:
        return "[kookit]"

    async def prepare_services(self, *services: IKookitService) -> None:
        logger.trace(f"{self}: preparing {len(services)} services: {services}")
        assert not self.services, "You can only add services once"
        for service in services:
            if not service.service_url:
                service.service_url = self.server.url

        self.services.extend(list(services))
        envs = {**os.environ}
        envs.update({s.url_env_var: s.service_url for s in services if s.url_env_var})
        envs.update()
        self.mocker.patch.dict(os.environ, envs)

    async def start_services(
        self,
        wait_for_server_launch: Optional[float] = None,
    ) -> None:
        assert not self.server_process
        self.server_process = Process(
            target=self.server.run,
            args=(self.services,),
        )
        logger.trace(f"{self}: starting server process")
        self.server_process.start()

        with suppress(queue.Empty):
            assert self.server_queue.get(timeout=wait_for_server_launch)

        logger.trace(f"{self}: running services")
        for service in self.services:
            await service.run()

    async def stop_services(
        self,
        wait_for_server_stop: Optional[float] = 0.0,
    ) -> None:
        logger.trace(f"{self}: stopping services")
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None

        try:
            await self.assert_completed(self.services)
        finally:
            self.services.clear()

        with suppress(queue.Empty):
            assert not self.server_queue.get(timeout=wait_for_server_stop)

    @staticmethod
    async def assert_completed(services: List[IKookitService]) -> None:
        service_unused_responses: dict = {
            service: service.unused_responses() for service in services
        }
        logger.debug(f"[kookit]: services' unused responses: {service_unused_responses}")
        assert not any(
            responses for responses in service_unused_responses.values()
        ), service_unused_responses

    async def __aenter__(self) -> "Kookit":
        return self

    async def __aexit__(self, *_args: Any) -> None:
        await self.stop_services()

    async def wait(self, seconds: float) -> None:
        await anyio.sleep(seconds)


@fixture
async def kookit(mocker: MockerFixture) -> AsyncIterator[Kookit]:
    async with Kookit(mocker) as kooky:
        yield kooky
