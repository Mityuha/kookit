from __future__ import annotations
import queue
from contextlib import suppress
from itertools import chain
from typing import Any, Dict, Final, Iterable, List, Tuple

from fastapi import APIRouter
from httpx import URL
from multiprocess import Process

from kookit import KookitHTTPServer
from ..logging import logger
from ..utils import ILifespan, Lifespans
from .actions_parser import groupby_actions
from .http_handler import KookitHTTPHandler
from .interfaces import IKookitHTTPRequest, IKookitHTTPResponse
from .request_runner import KookitHTTPRequestRunner


class KookitHTTPService:
    def __init__(
        self,
        *,
        server: KookitHTTPServer,
        actions: Iterable[IKookitHTTPRequest | IKookitHTTPResponse] = (),
        routers: Iterable[APIRouter] = (),
        lifespans: Iterable[ILifespan] = (),
        unique_url: bool = False,
        name: str = "",
    ) -> None:
        self.server: Final = server
        self.actions: list[IKookitHTTPRequest | IKookitHTTPResponse] = list(actions)
        self.routers: list[APIRouter] = list(routers)
        self.lifespan: Final = Lifespans(*list(lifespans))
        self._unique_url: Final = unique_url
        self._name: Final = name

        self.initial_requests: Final[List[IKookitHTTPRequest]] = []
        self.method_url_2_handler: Final[Dict[Tuple[str, URL], KookitHTTPHandler]] = {}

        # self.add_routers(*routers)
        # self.add_actions(*actions)
        self._server_process: Process | None = None

    @property
    def url(self) -> str:
        return self.server.url

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return f"[{self._name}]"

    def __repr__(self) -> str:
        return str(self)

    def add_lifespans(self, *lifespans: ILifespan) -> None:
        self.lifespan.add(*lifespans)

    def add_routers(self, *routers: APIRouter) -> None:
        self.routers.extend(routers)

    def start(self, *, wait_for_start_timeout: float | None = None) -> None:
        if not self._unique_url:
            return

        if self._server_process:
            logger.trace(f"{self}: server process already running")
            return

        logger.trace(f"{self}: starting server process [{self.url}]")
        self._server_process = Process(
            target=self.server.run,
            args=([self.routers], [self.lifespan]),
        )
        self._server_process.start()

        with suppress(queue.Empty):
            is_started = self.server.wait(wait_for_start_timeout)
            if not is_started:
                raise ValueError(f"{self}: bad value received from server while starting")

    def stop(self, *, wait_for_stop_timeout: float | None = None) -> None:
        if not self._unique_url:
            return

        if not self._server_process:
            logger.trace(f"{self}: server process already stopped")
            return

        logger.trace(f"{self}: stop server process")
        self._server_process.terminate()
        self._server_process = None

        with suppress(queue.Empty):
            is_started: bool = self.server.wait(wait_for_stop_timeout)
            if is_started:
                raise ValueError(f"{self}: bad value received from server while stopping")

    def __enter__(self) -> "KookitHTTPService":
        self.start()
        return self

    def __exit__(self, *_args: Any) -> None:
        self.stop()
        return

    async def __aenter__(self) -> "KookitHTTPService":
        self.start()
        return self

    async def __aexit__(self, *_args: Any) -> None:
        self.stop()
        return

    def calc_router(self) -> APIRouter:
        router = APIRouter()
        for router in self.routers:
            router.include_router(router)
        return router

    def add_actions(self, *actions: IKookitHTTPResponse | IKookitHTTPRequest) -> None:
        self.actions.extend(actions)

    def calc_actions(self) -> None:
        # self.initial_requests.extend(initial_requests(*actions))
        grouped_actions: list[Tuple[IKookitHTTPResponse, List[IKookitHTTPRequest]]] = (
            groupby_actions(*self.actions)
        )

        handlers: Iterable[KookitHTTPHandler] = (
            KookitHTTPHandler(
                resp,
                service_name=self.name,
                requests=requests,
            )
            for (resp, requests) in grouped_actions
        )

        for handler in handlers:
            url, method = handler.url, handler.method
            try:
                self.method_url_2_handler[(method, url)].merge(handler)
            except KeyError:
                self.method_url_2_handler[(method, url)] = handler

        for (method, url), handler in self.method_url_2_handler.items():
            self.router.add_api_route(
                url.path,
                handler.__call__,
                methods=[method],
            )
        logger.trace(
            f"{self}: handlers {self.method_url_2_handler}, {len(self.initial_requests)} initial requests {self.initial_requests}"
        )

    def unused_responses(self) -> List[IKookitHTTPResponse]:
        unused_responses: List[IKookitHTTPResponse] = list(
            chain.from_iterable(
                handler.unused_responses() for handler in self.method_url_2_handler.values()
            )
        )

        logger.trace(f"{self}: {len(unused_responses)} unused responses: {unused_responses}")
        return unused_responses

    async def run(self) -> None:
        runner: KookitHTTPRequestRunner = KookitHTTPRequestRunner(
            self.initial_requests,
            service_name=self.name,
        )
        await runner.run_requests()
