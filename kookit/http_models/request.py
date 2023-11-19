from typing import Any, Final, Mapping, Optional, Protocol, Union

from httpx import URL, Request
from httpx._types import HeaderTypes, QueryParamTypes, RequestContent, RequestData, RequestFiles


class IKookitService(Protocol):
    @property
    def service_url(self) -> str:
        ...


class KookitHTTPRequest:
    def __init__(
        self,
        service: IKookitService,
        *,
        url: Union[URL, str],
        method: Union[str, bytes],
        params: Optional[QueryParamTypes] = None,
        headers: Optional[HeaderTypes] = None,
        content: Optional[RequestContent] = None,
        data: Optional[RequestData] = None,
        files: Optional[RequestFiles] = None,
        json: Optional[Any] = None,
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
            json=json,
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
