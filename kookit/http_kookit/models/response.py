from __future__ import annotations
from dataclasses import dataclass
from json import dumps as json_dumps
from json import loads as json_loads
from typing import TYPE_CHECKING, Any, Final, Mapping

from httpx import URL, Request, Response

from kookit.utils import UUIDEncoder


if TYPE_CHECKING:
    from httpx._types import (
        HeaderTypes,
        QueryParamTypes,
        RequestContent,
        RequestData,
        RequestFiles,
    )


@dataclass
class KookitResponseRequest:
    content: bytes
    headers: Mapping[str, str] | None
    url: URL
    method: str


class KookitHTTPResponse:
    def __init__(
        self,
        url: URL | str,
        method: str | bytes,
        *,
        status_code: int = 200,
        http_version: str = "HTTP/1.1",
        headers: Mapping | None = None,
        content: bytes | None = None,
        text: str | None = None,
        html: str | None = None,
        json: Any = None,
        stream: Any = None,
        # Request matchers here
        request_params: QueryParamTypes | None = None,
        request_headers: HeaderTypes | None = None,
        request_content: RequestContent | None = None,
        request_data: RequestData | None = None,
        request_files: RequestFiles | None = None,
        request_json: Any | None = None,
    ) -> None:
        request = Request(
            url=url,
            method=method,
            params=request_params,
            headers=request_headers,
            content=request_content,
            data=request_data,
            files=request_files,
            json=json_loads(json_dumps(request_json, cls=UUIDEncoder)),
        )
        if request_headers:
            request_headers = request.headers  # lowercase headers' keys
        response: Response = Response(
            status_code=status_code,
            extensions={"http_version": http_version.encode("ascii")},
            headers=headers,
            json=json_loads(json_dumps(json, cls=UUIDEncoder)),
            content=content,
            text=text,
            html=html,
            stream=stream,
            request=request,
        )

        self.request: Final[KookitResponseRequest] = KookitResponseRequest(
            content=request.content,
            headers=request_headers,  # type: ignore[arg-type]
            url=request.url,
            method=request.method,
        )

        self.content: Final[bytes] = response.content
        self.headers: Final[Mapping[str, str]] = response.headers
        self.status_code: Final[int] = response.status_code

    def __str__(self) -> str:
        return f"<Response({self.status_code}, '{self.request.method}', '{self.request.url}')>"

    def __repr__(self) -> str:
        return str(self)
