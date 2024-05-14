from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Protocol


if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from fastapi import APIRouter
    from httpx import URL

    from kookit.utils import ILifespan


class IRequest(Protocol):
    @property
    def content(self) -> bytes: ...

    @property
    def headers(self) -> Mapping[str, str]: ...

    @property
    def url(self) -> URL: ...

    @property
    def method(self) -> str: ...

    @property
    def path_params(self) -> dict: ...


class IServer(Protocol):
    def wait(self, timeout: float | None = None) -> Any: ...
    def run(
        self,
        routers: Iterable[Callable[[], APIRouter]],
        lifespans: Iterable[ILifespan],
    ) -> None: ...

    @property
    def url(self) -> str: ...
