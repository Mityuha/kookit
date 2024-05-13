from __future__ import annotations
import queue
from contextlib import ExitStack, suppress
from itertools import groupby
from types import SimpleNamespace, TracebackType
from typing import TYPE_CHECKING, Any, Final

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from multiprocess import Process
from typing_extensions import Self

from kookit.logging import logger
from kookit.utils import ILifespan, Lifespans
from .models import KookitHTTPRequest, KookitHTTPResponse
from .response_group import ResponseGroup


if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from .interfaces import IServer


class KookitHTTPService:
    def __init__(
        self,
        *,
        server: IServer,
        actions: Iterable[KookitHTTPRequest | KookitHTTPResponse] = (),
        routers: Iterable[APIRouter] = (),
        lifespans: Iterable[ILifespan] = (),
        unique_url: bool = False,
        name: str = "",
        one_off: bool = True,
    ) -> None:
        self.server: Final = server
        self.actions: Final = list(actions)
        self.routers: Final = list(routers)
        self.lifespans: Final = list(lifespans)

        self._unique_url: Final = unique_url
        self._name: Final = name
        self._one_off: Final = one_off

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

    def __enter__(self) -> Self:
        self.start()
        return self

    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.stop(typ, exc, tb)

    async def __aenter__(self) -> Self:
        self.start()
        return self

    async def __aexit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.stop(typ, exc, tb)

    def add_actions(self, *actions: KookitHTTPResponse | KookitHTTPRequest) -> None:
        self.actions.extend(actions)

    def add_lifespans(self, *lifespans: ILifespan) -> None:
        self.lifespans.extend(lifespans)

    def add_routers(self, *routers: APIRouter) -> None:
        self.routers.extend(routers)

    @property
    def router(self) -> APIRouter:
        router = APIRouter()
        for r in self.routers:
            router.include_router(r)

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

        logger.trace(
            f"{self}: waiting for server process to start ({wait_for_start_timeout} seconds)",
        )
        with suppress(queue.Empty):
            is_started = self.server.wait(wait_for_start_timeout)
            if not is_started:
                msg = f"{self}: bad value received from server while starting"
                raise ValueError(msg)
        logger.trace(f"{self}: server process successfully started")

    def stop(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
        *,
        wait_for_stop_timeout: float | None = None,
    ) -> None:
        if self._one_off:
            self.actions.clear()
            self.routers.clear()
            self.lifespans.clear()

        if self._unique_url and self._server_process:
            logger.trace(f"{self}: stop server process")
            self._server_process.terminate()
            self._server_process = None

            with suppress(queue.Empty):
                is_started: bool = self.server.wait(wait_for_stop_timeout)
                if is_started:
                    msg = f"{self}: bad value received from server while stopping"
                    raise ValueError(msg)

        active_groups = [group for group in self._response_groups if group.active]
        if active_groups and not any([exc_type, exc_val, exc_tb]):
            msg = f"{self}: active groups left: {', '.join(str(g) for g in active_groups)}"
            raise RuntimeError(
                msg,
            )

        self._response_groups = []

    @staticmethod
    def create_response_groups(
        actions: Iterable[KookitHTTPRequest | KookitHTTPResponse],
        *,
        parent: Any = "",
    ) -> Sequence[ResponseGroup]:
        groups: list[ResponseGroup] = []
        for is_request, group in groupby(
            actions,
            key=lambda key: isinstance(key, KookitHTTPRequest),
        ):
            if is_request:
                if not groups:
                    groups.append(ResponseGroup(parent=parent))
                groups[-1].add_requests(*group)  # type: ignore[arg-type]
            else:
                groups.extend(ResponseGroup(response, parent=parent) for response in group)  # type: ignore[arg-type]

        return groups

    async def __call__(self, request: Request) -> Response:
        group: ResponseGroup | None = None
        cmp_request = SimpleNamespace(
            content=await request.body(),
            headers=request.headers,
            url=request.url,
            method=request.method,
            path_params=request.path_params,
        )
        for gr in self._response_groups:
            if gr == cmp_request:
                group = gr
                break

        if not group:
            return JSONResponse(
                {"error": f"{self}: cannot find response for request: {request}"},
                status_code=400,
            )

        with group:
            if not group.response:
                msg = "Response group should specify response"
                raise ValueError(msg)
            return Response(
                content=group.response.content,
                media_type=group.response.headers["content-type"],
                headers=group.response.headers,
                status_code=group.response.status_code,
            )
