from typing import Any, Final, Mapping, Optional, Union

from httpx import URL, Request, Response
from httpx._types import HeaderTypes, QueryParamTypes, RequestContent, RequestData, RequestFiles


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
        self.response: Final[Response] = Response(
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
