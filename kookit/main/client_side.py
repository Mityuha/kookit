from typing import Any, Protocol

from httpx import AsyncClient, Response


class IKookitService(Protocol):
    @property
    def service_url(self) -> str:
        ...


class KookitHTTPAsyncClient:
    async def request(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        async with AsyncClient(base_url=service.service_url) as client:
            return await client.request(*args, **kwargs)

    async def get(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return await self.request(service, "GET", *args, **kwargs)

    async def post(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return await self.request(service, "POST", *args, **kwargs)

    async def put(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return await self.request(service, "PUT", *args, **kwargs)

    async def delete(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return await self.request(service, "DELETE", *args, **kwargs)

    async def options(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return await self.request(service, "OPTIONS", *args, **kwargs)

    async def patch(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return await self.request(service, "PATCH", *args, **kwargs)

    async def head(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return await self.request(service, "HEAD", *args, **kwargs)
