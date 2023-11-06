from contextlib import suppress
from typing import Final, List, Optional

from httpx import AsyncClient, RequestError

from .interfaces import IKookitHTTPRequest


class KookitHTTPRequestRunner:
    def __init__(
        self,
        requests: Optional[List[IKookitHTTPRequest]] = None,
    ) -> None:
        self.requests: Final[List[IKookitHTTPRequest]] = requests or []

    async def run_requests(self) -> None:
        for req in self.requests:
            r = req.request
            async with AsyncClient(base_url=req.service.service_url) as client:
                with suppress(RequestError):
                    await client.request(
                        method=r.method,
                        url=r.url,
                        content=r.content,
                        headers=r.headers,
                    )
