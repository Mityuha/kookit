from typing import Any, Mapping, Optional

from .http_response import KookitHTTPResponse


class KookitJSONResponse(KookitHTTPResponse):
    def __init__(
        self,
        json: Any,
        *,
        url: str = "/",
        method: str = "GET",
        status_code: int = 200,
        headers: Optional[Mapping] = None,
    ) -> None:
        super().__init__(
            json=json,
            status_code=status_code,
            method=method,
            headers=headers,
            url=url,
        )
