from typing import Final, List, Optional

from httpx import AsyncClient, RequestError, Response

from ..logging import logger
from .interfaces import IKookitHTTPRequest


class KookitHTTPRequestRunner:
    def __init__(
        self,
        requests: Optional[List[IKookitHTTPRequest]] = None,
        *,
        service_name: str,
    ) -> None:
        self.requests: Final[List[IKookitHTTPRequest]] = requests or []
        self.service_name: Final[str] = service_name

    def __str__(self) -> str:
        return f"[{self.service_name}][Request]"

    async def run_requests(self) -> List[Response]:
        logger.trace(f"{self}: running {len(self.requests)} requests")
        responses: List[Response] = []
        for req in self.requests:
            r = req.request
            logger.debug(f"{self}: running request {r} ({req.service.service_url})")
            async with AsyncClient(base_url=req.service.service_url) as client:
                try:
                    response = await client.request(
                        method=r.method,
                        url=r.url,
                        content=r.content,
                        headers=r.headers,
                    )
                    responses.append(response)
                except (RequestError, Exception) as exc:
                    logger.error(f"{self}: error: cannot execute {r}: {exc}")
                else:
                    logger.debug(f"{self}: request {r} successfully executed: {response}")

        return responses
