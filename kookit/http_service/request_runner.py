import asyncio
from typing import Any, Final, List, Optional

from httpx import AsyncClient, Response

from ..logging import logger
from .interfaces import IKookitHTTPRequest


class KookitHTTPRequestRunner:
    def __init__(
        self,
        requests: Optional[List[IKookitHTTPRequest]] = None,
        *,
        service_name: str,
        run_in_background: bool = False,
    ) -> None:
        self.requests: Final[List[IKookitHTTPRequest]] = requests or []
        self.service_name: Final[str] = service_name
        self.run_in_background: Final[bool] = run_in_background

    def __str__(self) -> str:
        return f"[{self.service_name}][Request]"

    async def run_request(
        self,
        *,
        base_url: str,
        url: Any,
        method: str,
        content: bytes,
        headers: Any,
        request_delay: float,
    ) -> Response:
        logger.debug(f"{self}: running request <{method} {url}> ({base_url=}, {request_delay=}))")
        await asyncio.sleep(request_delay)
        async with AsyncClient(base_url=base_url) as client:
            response = await client.request(
                method=method,
                url=url,
                content=content,
                headers=headers,
            )

        logger.debug(f"{self}: request <{method} {url}> successfully executed: {response}")
        return response

    async def _run_requests(self) -> List[Response]:
        logger.trace(f"{self}: running {len(self.requests)} requests")
        responses: List[Response] = await asyncio.gather(
            *[
                self.run_request(
                    base_url=req.service.service_url,
                    url=req.url,
                    method=req.method,
                    content=req.content,
                    headers=req.headers,
                    request_delay=req.request_delay,
                )
                for req in self.requests
            ],
            return_exceptions=True,
        )

        for request, response in zip(self.requests, responses):
            if isinstance(response, BaseException):
                logger.error(f"{self}: error: cannot execute {request}: {response}")

        return [r for r in responses if not isinstance(r, BaseException)]

    async def run_requests(self) -> List[Response]:
        if not self.run_in_background:
            return await self._run_requests()

        asyncio.create_task(self._run_requests())
        return []
