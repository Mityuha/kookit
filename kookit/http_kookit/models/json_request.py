from __future__ import annotations
from typing import Any, Mapping

from .request import URL, IKookitService, KookitHTTPRequest, QueryParamTypes


class KookitJSONRequest(KookitHTTPRequest):
    def __init__(
        self,
        service: IKookitService,
        *,
        json: Any,
        url: str | URL = "/",
        method: str = "POST",
        headers: Mapping | None = None,
        params: QueryParamTypes | None = None,
        request_delay: float = 0.0,
    ) -> None:
        super().__init__(
            service,
            json=json,
            method=method,
            headers=headers,
            url=url,
            params=params,
            request_delay=request_delay,
        )
