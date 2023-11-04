from typing import Any, Final, Mapping, Optional, Union

from httpx import URL, Request, Response


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
    ) -> None:
        request = Request(
            url=url,
            method=method,
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
