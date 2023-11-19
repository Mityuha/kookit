from dataclasses import dataclass
from typing import Any, Final, Mapping, Optional, Union

from httpx import URL, Request, Response
from httpx._types import HeaderTypes, QueryParamTypes, RequestContent, RequestData, RequestFiles


@dataclass
class KookitResponseRequest:
    content: bytes
    headers: Optional[Mapping[str, str]]
    url: URL
    method: str


class KookitHTTPResponse:
    def __init__(
        self,
        url: Union[URL, str],
        method: Union[str, bytes],
        *,
        status_code: int = 200,
        http_version: str = "HTTP/1.1",
        headers: Optional[Mapping] = None,
        content: Optional[bytes] = None,
        text: Optional[str] = None,
        html: Optional[str] = None,
        json: Any = None,
        stream: Any = None,
        # Request matchers here
        request_params: Optional[QueryParamTypes] = None,
        request_headers: Optional[HeaderTypes] = None,
        request_content: Optional[RequestContent] = None,
        request_data: Optional[RequestData] = None,
        request_files: Optional[RequestFiles] = None,
        request_json: Optional[Any] = None,
    ) -> None:
        request = Request(
            url=url,
            method=method,
            params=request_params,
            headers=request_headers,
            content=request_content,
            data=request_data,
            files=request_files,
            json=request_json,
        )
        response: Response = Response(
            status_code=status_code,
            extensions={"http_version": http_version.encode("ascii")},
            headers=headers,
            json=json,
            content=content,
            text=text,
            html=html,
            stream=stream,
            request=request,
        )

        self.request: Final[KookitResponseRequest] = KookitResponseRequest(
            content=request.content,
            headers=request_headers,  # type: ignore
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
