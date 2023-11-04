import os
from typing import Any, AsyncIterator, Final, List, Optional

from multiprocess import Process
from pytest import fixture
from pytest_mock import MockerFixture

from .interfaces import IKookitService
from .server import KookitServer


class Kookit:
    def __init__(self, mocker: MockerFixture) -> None:
        self.mocker: Final[MockerFixture] = mocker
        self.server: Final[KookitServer] = KookitServer()
        self.services: Final[List[IKookitService]] = []
        self.server_process: Optional[Process] = None

    def add_services(self, *services: IKookitService) -> None:
        assert not self.services, "You can only add services only once"
        self.services.extend(list(services))
        envs = {**os.environ}
        envs.update({s.url_env_var: self.server.url for s in services if s.url_env_var})
        envs.update()
        self.mocker.patch.dict(os.environ, envs)

    async def start_services(self) -> None:
        assert not self.server_process
        self.server_process = Process(
            target=self.server.run,
            args=(self.services,),
        )
        self.server_process.start()
        for service in self.services:
            await service.run()

    async def stop_services(self) -> None:
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None

        self.services.clear()

    async def __aenter__(self) -> "Kookit":
        return self

    async def __aexit__(self, *_args: Any) -> None:
        await self.stop_services()


@fixture
async def kookit(mocker: MockerFixture) -> AsyncIterator[Kookit]:
    async with Kookit(mocker) as ko:
        yield ko
