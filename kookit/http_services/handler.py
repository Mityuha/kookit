from typing import Final, List, Optional

from fastapi import Response as FastAPIResponse
from httpx import Response

from ..http_responses import KookitHTTPCallback


class KookitHTTPHandler:
    def __init__(
        self, response: Response, *, callbacks: Optional[List[KookitHTTPCallback]] = None
    ) -> None:
        self.r: Final[Response] = response
        self.response: Final[FastAPIResponse] = FastAPIResponse(
            content=response.content,
            media_type=response.headers["content-type"],
            headers=response.headers,
            status_code=response.status_code,
        )
        self.callback_runner: Final[KookitHTTPCallbackRunner] = KookitHTTPCallbackRunner(callbacks)

    async def run_callbacks(self) -> None:
        await self.callback_runner.run_callbacks()


class KookitHTTPCallbackRunner:
    def __init__(
        self,
        callbacks: Optional[List[KookitHTTPCallback]] = None,
    ) -> None:
        self.callbacks: Final[List[KookitHTTPCallback]] = callbacks or []

    async def run_callbacks(self) -> None:
        ...
