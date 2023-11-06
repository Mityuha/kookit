from dataclasses import dataclass
from typing import Final, List, Optional
from urllib.parse import parse_qs, urlparse

from fastapi import Request as FastAPIRequest
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse
from httpx import Request, Response
from multiprocess import Value

from .interfaces import IKookitHTTPRequest
from .request_runner import KookitHTTPRequestRunner


@dataclass
class ResponseWithCallbacks:
    request: Request
    response: Response
    request_runner: KookitHTTPRequestRunner


class KookitHTTPHandler:
    def __init__(
        self,
        response: Response,
        *,
        requests: Optional[List[IKookitHTTPRequest]] = None,
    ) -> None:
        self.url: Final[str] = str(response.request.url)
        self.method: Final[str] = response.request.method
        self.responses: Final[List[ResponseWithCallbacks]] = [
            ResponseWithCallbacks(
                request=response.request,
                response=response,
                request_runner=KookitHTTPRequestRunner(requests),
            )
        ]
        self.current_response: Value = Value("i", 0)

    @staticmethod
    async def compare_requests(
        frequest: FastAPIRequest,
        request: Request,
    ) -> str:
        content = request.content
        fcontent = await frequest.body()
        if content != fcontent:
            return f"Expected body: '{content!r}', got: '{fcontent!r}'"

        if not all(it in frequest.headers.items() for it in request.headers.items()):
            return (
                f"Expected headers present: {dict(request.headers)}, got: {dict(frequest.headers)}"
            )

        parsed_url = urlparse(str(request.url))
        parsed_furl = urlparse(str(frequest.url))

        assert parsed_url.path == parsed_furl.path

        if parsed_url.query and parse_qs(parsed_url.query) != parse_qs(parsed_furl.query):
            return f"Expected query params: '{parsed_url.query}', got: '{parsed_furl.query}'"

        return ""

    async def __call__(self, request: FastAPIRequest) -> FastAPIResponse:
        if self.current_response.value >= len(self.responses):
            return JSONResponse(
                content={
                    "error": f"Got an extra request for '{self.method} {self.url}', but no more responses left for requests"
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

        await response_and_callbacks.request_runner.run_requests()
        return fastapi_response

    def merge(self, other: "KookitHTTPHandler") -> None:
        assert self.url == other.url
        assert self.method == other.method
        self.responses.extend(other.responses)

    def assert_completed(self, service_name: str) -> None:
        unused_responses: int = len(self.responses) - self.current_response.value
        assert (
            not unused_responses
        ), f"Handler '{service_name} {self.method} {self.url}': {unused_responses} unused responses left"
