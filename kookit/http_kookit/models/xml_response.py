from typing import Any, Mapping, Optional

from .response import KookitHTTPResponse


class KookitXMLResponse(KookitHTTPResponse):
    def __init__(
        self,
        xml: Any,
        *,
        url: str = "/",
        method: str = "GET",
        status_code: int = 200,
        headers: Optional[Mapping] = None,
        **request_matchers: Any,
    ) -> None:
        headers = headers or {}
        headers = dict(headers)
        headers["content-type"] = "application/xml"
        super().__init__(
            text=xml,
            status_code=status_code,
            method=method,
            headers=headers,
            url=url,
            **request_matchers,
        )
