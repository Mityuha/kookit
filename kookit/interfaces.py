from __future__ import annotations
from typing import TYPE_CHECKING, Any, Protocol


if TYPE_CHECKING:
    from types import TracebackType

    from fastapi import APIRouter

    from .http_kookit import KookitHTTPRequest, KookitHTTPResponse
    from .utils import ILifespan


class IKookitHTTPService(Protocol):
    @property
    def url(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def __enter__(self) -> Any: ...
    def __exit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
    async def __aenter__(self) -> Any: ...
    async def __aexit__(
        self,
        typ: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
    def add_actions(self, *actions: KookitHTTPResponse | KookitHTTPRequest) -> None: ...
    def add_lifespans(self, *lifespans: ILifespan) -> None: ...
    def add_routers(self, *routers: APIRouter) -> None: ...
    def start(self) -> None: ...
    def stop(
        self,
        exc_type: type[BaseException] | None = None,
        exc_val: BaseException | None = None,
        exc_tb: TracebackType | None = None,
    ) -> None: ...
