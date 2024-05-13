from __future__ import annotations
from typing import Any, Mapping

from .response import KookitHTTPResponse


class KookitJSONResponse(KookitHTTPResponse):
    def __init__(
        self,
        json: Any,
        *,
        url: str = "/",
        method: str = "GET",
        status_code: int = 200,
        headers: Mapping | None = None,
        **request_matchers: Any,
    ) -> None:
        super().__init__(
            json=json,
            status_code=status_code,
            method=method,
            headers=headers,
            url=url,
            **request_matchers,
        )
