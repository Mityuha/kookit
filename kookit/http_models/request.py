from typing import Any, Final, Optional, Protocol, Union

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
    ) -> None:
        self.service: Final[IKookitService] = service
        self.request: Final[Request] = Request(
            url=url,
            method=method,
            params=params,
            headers=headers,
            content=content,
            data=data,
            files=files,
            json=json,
        )