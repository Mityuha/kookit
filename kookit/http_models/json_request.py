from typing import Any, Mapping, Optional, Union

from .request import URL, IKookitService, KookitHTTPRequest, QueryParamTypes


class KookitJSONRequest(KookitHTTPRequest):
    def __init__(
        self,
        service: IKookitService,
        *,
        json: Any,
        url: Union[str, URL] = "/",
        method: str = "POST",
        headers: Optional[Mapping] = None,
        params: Optional[QueryParamTypes] = None,
    ) -> None:
        super().__init__(
            service,
            json=json,
            method=method,
            headers=headers,
            url=url,
            params=params,
        )
