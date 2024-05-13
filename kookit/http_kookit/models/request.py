from __future__ import annotations
from json import dumps as json_dumps
from json import loads as json_loads
from typing import TYPE_CHECKING, Any, Final, Mapping, Protocol

from httpx import URL, Request

from kookit.utils import UUIDEncoder


if TYPE_CHECKING:
    from httpx._types import (
        HeaderTypes,
        QueryParamTypes,
        RequestContent,
        RequestData,
        RequestFiles,
    )


class IKookitService(Protocol):
    @property
    def url(self) -> str: ...


class KookitHTTPRequest:
    def __init__(
        self,
        service: IKookitService,
        *,
        url: URL | str,
        method: str | bytes,
        params: QueryParamTypes | None = None,
        headers: HeaderTypes | None = None,
        content: RequestContent | None = None,
        data: RequestData | None = None,
        files: RequestFiles | None = None,
        json: Any | None = None,
        request_delay: float = 0.0,
    ) -> None:
        self.service: Final[IKookitService] = service
        request: Request = Request(
            url=url,
            method=method,
            params=params,
            headers=headers,
            content=content,
            data=data,
            files=files,
            json=json_loads(json_dumps(json, cls=UUIDEncoder)),
        )
        self.url: Final[URL] = request.url
        self.method: Final[str] = request.method
        self.content: Final[bytes] = request.content
        self.headers: Mapping[str, str] = request.headers
        self.request_delay: Final[float] = request_delay

    def __str__(self) -> str:
        return f"<Request({self.service}, '{self.method}', '{self.url}')>"

    def __repr__(self) -> str:
        return str(self)
