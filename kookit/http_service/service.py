from __future__ import annotations
import queue
from collections.abc import Iterable, Sequence
from contextlib import ExitStack, suppress
from itertools import groupby
from typing import Any, Final

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from multiprocess import Process

from kookit import KookitHTTPServer
from ..http_models import KookitHTTPRequest, KookitHTTPResponse
from ..logging import logger
from ..utils import ILifespan, Lifespans
from .response_group import ResponseGroup


class KookitHTTPService:
    def __init__(
        self,
        *,
        server: KookitHTTPServer,
        actions: Iterable[KookitHTTPRequest | KookitHTTPResponse] = (),
        routers: Iterable[APIRouter] = (),
        lifespans: Iterable[ILifespan] = (),
        unique_url: bool = False,
        name: str = "",
    ) -> None:
        self.server: Final = server
        self.actions: Final = list(actions)
        self.routers: Final = list(routers)
        self.lifespans: Final = list(lifespans)

        self._unique_url: Final = unique_url
        self._name: Final = name
        self._server_process: Process | None = None
        self._response_groups: Sequence[ResponseGroup] = []

    @property
    def url(self) -> str:
        return self.server.url

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_url(self) -> bool:
        return self._unique_url

    def __str__(self) -> str:
        return f"[{self._name}]"

    def __repr__(self) -> str:
        return str(self)

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

    def add_actions(self, *actions: KookitHTTPResponse | KookitHTTPRequest) -> None:
        self.actions.extend(actions)

    def add_lifespans(self, *lifespans: ILifespan) -> None:
        self.lifespans.extend(lifespans)

    def add_routers(self, *routers: APIRouter) -> None:
        self.routers.extend(routers)

    @property
    def router(self) -> APIRouter:
        router = APIRouter()
        for router in self.routers:
            router.include_router(router)

        for group in self._response_groups:
            if group.response:
                router.add_api_route(
                    group.path,
                    self.__call__,
                    methods=[group.method],
                )
        return router

    @property
    def lifespan(self) -> ILifespan:
        return Lifespans(*self.lifespans)

    def start(self, *, wait_for_start_timeout: float | None = None) -> None:
        if self._response_groups:
            logger.trace(f"{self}: service already started")
            return

        self._response_groups = self.create_response_groups(self.actions, parent=self)

        with ExitStack() as stack:
            _ = [
                stack.enter_context(group) for group in self._response_groups if not group.response
            ]

        if not self._unique_url:
            return

        if self._server_process:
            logger.trace(f"{self}: server process already running")
            return

        logger.trace(f"{self}: starting server process [{self.url}]")
        self._server_process = Process(
            target=self.server.run,
            args=([self.router], [self.lifespan]),
        )
        self._server_process.start()

        with suppress(queue.Empty):
            is_started = self.server.wait(wait_for_start_timeout)
            if not is_started:
                raise ValueError(f"{self}: bad value received from server while starting")

    def stop(self, *, wait_for_stop_timeout: float | None = None) -> None:
        self.actions.clear()
        self.routers.clear()
        self.lifespans.clear()

        active_groups = [group for group in self._response_groups if group.active]
        if active_groups:
            raise RuntimeError(
                f"{self}: active groups left: {', '.join(str(g) for g in active_groups)}"
            )

        self._response_groups = []

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

    @staticmethod
    def create_response_groups(
        actions: Iterable[KookitHTTPRequest | KookitHTTPResponse],
        *,
        parent: Any = "",
    ) -> Sequence[ResponseGroup]:
        groups: list[ResponseGroup] = []
        for is_request, group in groupby(
            actions, key=lambda key: isinstance(key, KookitHTTPRequest)
        ):
            if is_request:
                if not groups:
                    groups.append(ResponseGroup(parent=parent))
                groups[-1].add_requests(*group)  # type: ignore
            else:
                groups.extend(ResponseGroup(response, parent=parent) for response in group)  # type: ignore

        return groups

    async def __call__(self, request: Request) -> Response:
        group: ResponseGroup | None = None
        for gr in self._response_groups:
            if gr == request:
                break

        if not group:
            return JSONResponse(
                {"error": f"{self}: cannot find response for request: {request}"}, status_code=400
            )

        with group:
            assert group.response
            return Response(
                content=group.response.content,
                media_type=group.response.headers["content-type"],
                headers=group.response.headers,
                status_code=group.response.status_code,
            )
