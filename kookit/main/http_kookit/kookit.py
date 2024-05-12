import os
import queue
from contextlib import AbstractAsyncContextManager, suppress
from itertools import cycle
from typing import Any, Final, Iterable, Optional

from fastapi import APIRouter
from multiprocess import Process
from pytest_mock import MockerFixture

from kookit.logging import logger
from ..http_models import KookitHTTPRequest, KookitHTTPResponse
from ..http_service import KookitHTTPService
from .interfaces import IKookitHTTPService
from .server import KookitHTTPServer


class HTTPKookit:
    server_port: Final[cycle] = cycle(i for i in range(29000, 30000))

    def __init__(self, mocker: MockerFixture) -> None:
        self.mocker: Final[MockerFixture] = mocker
        self.server: Final[KookitHTTPServer] = KookitHTTPServer(next(self.server_port))
        self.services: Final[list[KookitHTTPService]] = []
        self.server_process: Optional[Process] = None

    def __str__(self) -> str:
        return "[HTTPKookit]"

    def new_service(
        self,
        env_var: str,
        *,
        unique_url: bool,
        actions: Iterable[KookitHTTPRequest | KookitHTTPResponse] = (),
        routers: Iterable[APIRouter] = (),
        lifespans: Iterable[AbstractAsyncContextManager] = (),
        name: str = "",
    ) -> IKookitHTTPService:
        server = self.server
        if unique_url:
            server = KookitHTTPServer(
                next(self.server_port),
            )

        if env_var:
            self.mocker.patch.dict(os.environ, {"env_var": server.url})
        service = KookitHTTPService(
            server=server,
            actions=actions,
            routers=routers,
            lifespans=lifespans,
            name=name,
        )
        self.services.append(service)
        return service

    def __enter__(self) -> "KookitHTTPService":
        not_unique = []
        for service in self.services:
            service.start()
            if not service.unique_url:
                not_unique.append(service)

        if not not_unique or self.server_process:
            return

        self.server_process = Process(
            target=self.server.run,
            args=([s.router for s in not_unique], [s.lifespan for s in not_unique]),
        )
        self.server_process.start()

        with suppress(queue.Empty):
            is_started = self.server.wait()
            if not is_started:
                raise ValueError(f"{self}: bad value received from server while starting")

    def __exit__(self, *_args: Any) -> None:
        for service in self.services:
            service.stop()

        if not self.server_process:
            logger.trace(f"{self}: server process already stopped")
            return

        logger.trace(f"{self}: stop server process")
        self.server_process.terminate()
        self.server_process = None

        with suppress(queue.Empty):
            is_started: bool = self.server.wait()
            if is_started:
                raise ValueError(f"{self}: bad value received from server while stopping")

    # async def prepare_services(self, *services: Any) -> List[Any]:
    #     assert not self.services, "You can only add services once"
    #     logger.trace(f"{self}: preparing {len(services)} services: {services}")
    #     self.services.extend((service for service in services if http_service(service)))
    #     for service in self.services:
    #         if not service.service_url:
    #             service.service_url = self.server.url

    #     envs = {**os.environ}
    #     envs.update({s.url_env_var: s.service_url for s in services if s.url_env_var})
    #     envs.update()
    #     self.mocker.patch.dict(os.environ, envs)
    #     return [service for service in services if not http_service(service)]

    # async def start_services(
    #     self,
    #     **kwargs: Any,
    # ) -> None:
    #     assert not self.server_process
    #     self.server_process = Process(
    #         target=self.server.run,
    #         args=(self.services,),
    #     )
    #     logger.trace(f"{self}: starting server process")
    #     self.server_process.start()

    #     wait_for_server_launch: Optional[float] = kwargs.get("http_wait_for_server_launch")
    #     with suppress(queue.Empty):
    #         assert self.server_queue.get(timeout=wait_for_server_launch)

    #     logger.trace(f"{self}: running services")
    #     for service in self.services:
    #         await service.run()

    # async def stop_services(self, **kwargs: Any) -> None:
    #     logger.trace(f"{self}: stopping services")
    #     if self.server_process:
    #         self.server_process.terminate()
    #         self.server_process = None

    #     try:
    #         await self.assert_completed(self.services, local_url=self.server.url)
    #     finally:
    #         self.services.clear()

    #     wait_for_server_stop: Optional[float] = kwargs.get("http_wait_for_server_stop")
    #     with suppress(queue.Empty):
    #         assert not self.server_queue.get(timeout=wait_for_server_stop)

    # @staticmethod
    # async def assert_completed(
    #     services: List[IKookitHTTPService],
    #     local_url: str,
    # ) -> None:
    #     service_unused_responses: dict = {
    #         service: service.unused_responses() for service in services
    #     }
    #     logger.debug(f"[kookit]: services' unused responses: {service_unused_responses}")
    #     assert not any(
    #         responses
    #         for service, responses in service_unused_responses.items()
    #         if service.service_url == local_url
    #     ), service_unused_responses
