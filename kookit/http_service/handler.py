from dataclasses import dataclass
from typing import Final, List, Optional

from fastapi import Request as FastAPIRequest
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse
from httpx import Request, Response
from multiprocess import Value

from ..http_response import KookitHTTPCallback


@dataclass
class ResponseWithCallbacks:
    request: Request
    response: Response
    callback_runner: "KookitHTTPCallbackRunner"


class KookitHTTPHandler:
    def __init__(
        self,
        response: Response,
        *,
        callbacks: Optional[List[KookitHTTPCallback]] = None,
    ) -> None:
        self.url: Final[str] = str(response.request.url)
        self.method: Final[str] = response.request.method
        self.responses: Final[List[ResponseWithCallbacks]] = [
            ResponseWithCallbacks(
                request=response.request,
                response=response,
                callback_runner=KookitHTTPCallbackRunner(callbacks),
            )
        ]
        self.current_response: Value = Value("i", 0)

    @staticmethod
    async def compare_requests(
        frequest: FastAPIRequest,
        request: Request,
    ) -> str:
        return ""

    async def __call__(self, request: FastAPIRequest) -> FastAPIResponse:
        if self.current_response.value >= len(self.responses):
            return JSONResponse(
                content={
                    "error": "Got an extra request for '{self.method} {self.url}', but no more responses left for requests"
                },
                status_code=418,
            )
        response_and_callbacks: ResponseWithCallbacks = self.responses[self.current_response.value]

        diff: str = await self.compare_requests(
            request,
            response_and_callbacks.request,
        )
        if diff:
            return JSONResponse({"error": diff}, status_code=400)

        response = response_and_callbacks.response
        fastapi_response: FastAPIResponse = FastAPIResponse(
            content=response.content,
            media_type=response.headers["content-type"],
            headers=response.headers,
            status_code=response.status_code,
        )

        with self.current_response.get_lock():
            self.current_response.value += 1

        await response_and_callbacks.callback_runner.run_callbacks()
        return fastapi_response

    def merge(self, other: "KookitHTTPHandler") -> None:
        assert self.url == other.url
        assert self.method == other.method
        self.responses.extend(other.responses)

    def assert_completed(self) -> None:
        unused_responses: int = len(self.responses) - self.current_response.value
        assert (
            not unused_responses
        ), f"Handler '{self.method} {self.url}: {unused_responses} unused responses left"


class KookitHTTPCallbackRunner:
    def __init__(
        self,
        callbacks: Optional[List[KookitHTTPCallback]] = None,
    ) -> None:
        self.callbacks: Final[List[KookitHTTPCallback]] = callbacks or []

    async def run_callbacks(self) -> None:
        ...
