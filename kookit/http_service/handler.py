from dataclasses import dataclass
from typing import Final, List, Optional
from urllib.parse import unquote

from fastapi import Request as FastAPIRequest
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse
from httpx import Request, Response
from multiprocess import Value

from ..logging import logger
from .interfaces import IKookitHTTPRequest
from .request_runner import KookitHTTPRequestRunner
from .requests_diff import compare_requests


@dataclass
class ReqRespRunner:
    request: Request
    response: Response
    request_runner: KookitHTTPRequestRunner


class KookitHTTPHandler:
    def __init__(
        self,
        response: Response,
        *,
        service_name: str,
        requests: Optional[List[IKookitHTTPRequest]] = None,
    ) -> None:
        # TODO: source url is needed here, not request.url
        self.url: Final[str] = unquote(str(response.request.url))
        self.method: Final[str] = response.request.method
        self.responses: Final[List[ReqRespRunner]] = [
            ReqRespRunner(
                request=response.request,
                response=response,
                request_runner=KookitHTTPRequestRunner(
                    requests,
                    service_name=service_name,
                ),
            )
        ]
        self.current_response: Value = Value("i", 0)
        self.service_name: Final[str] = service_name

    def __str__(self) -> str:
        responses_left: int = len(self.responses) - self.current_response.value
        return f"<Handler([{self.service_name}], '{self.method}', '{self.url}', total={len(self.responses)}, left={responses_left})>"

    def __repr__(self) -> str:
        return str(self)

    async def __call__(self, request: FastAPIRequest) -> FastAPIResponse:
        if self.current_response.value >= len(self.responses):
            logger.error(f"{self}: No more responses left")
            return JSONResponse(
                content={
                    "error": f"Got an extra request for '{self.method} {self.url}', but no more responses left for requests"
                },
                status_code=418,
            )
        info: ReqRespRunner = self.responses[self.current_response.value]

        diff: str = await compare_requests(
            request,
            info.request,
        )
        if diff:
            logger.error(f"{self}: unexpected request: {diff}")
            return JSONResponse({"error": diff}, status_code=400)

        logger.trace(f"{self}: requests matched")

        response = info.response
        fastapi_response: FastAPIResponse = FastAPIResponse(
            content=response.content,
            media_type=response.headers["content-type"],
            headers=response.headers,
            status_code=response.status_code,
        )

        with self.current_response.get_lock():
            self.current_response.value += 1

        logger.trace(f"{self}: running requests")
        await info.request_runner.run_requests()
        return fastapi_response

    def merge(self, other: "KookitHTTPHandler") -> None:
        assert self.url == other.url
        assert self.method == other.method
        self.responses.extend(other.responses)

    def unused_responses(self) -> List[Response]:
        unused_responses = [
            self.responses[i].response
            for i in range(self.current_response.value, len(self.responses))
        ]
        logger.trace(f"{self}: {len(unused_responses)} unused responses: {unused_responses}")
        return unused_responses
