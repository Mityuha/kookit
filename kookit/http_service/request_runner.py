from typing import Final, List, Optional

from httpx import AsyncClient, RequestError

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

    async def run_requests(self) -> None:
        print(f"{self}: running {len(self.requests)} requests")
        for req in self.requests:
            r = req.request
            print(f"{self}: running request {r} ({req.service.service_url})")
            async with AsyncClient(base_url=req.service.service_url) as client:
                try:
                    response = await client.request(
                        method=r.method,
                        url=r.url,
                        content=r.content,
                        headers=r.headers,
                    )
                except (RequestError, Exception) as exc:
                    print(f"{self}: error: cannot execute {r}: {exc}")
                else:
                    print(f"{self}: request {r} successfully executed: {response}")
