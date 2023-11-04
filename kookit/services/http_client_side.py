from typing import Any, Final

from fastapi import APIRouter, FastAPI
from httpx import AsyncClient, Response


class KookitHTTPClientSide:
    def __init__(self, router: APIRouter) -> None:
        self._router: Final[APIRouter] = router

    async def request(self, *args: Any, **kwargs: Any) -> Response:
        app = FastAPI()
        app.include_router(self._router)
        async with AsyncClient(app=app, base_url="https://base.url") as client:
            return await client.request(*args, **kwargs)

    async def get(self, *args: Any, **kwargs: Any) -> Response:
        return await self.request("GET", *args, **kwargs)

    async def post(self, *args: Any, **kwargs: Any) -> Response:
        return await self.request("POST", *args, **kwargs)

    async def put(self, *args: Any, **kwargs: Any) -> Response:
        return await self.request("PUT", *args, **kwargs)

    async def delete(self, *args: Any, **kwargs: Any) -> Response:
        return await self.request("DELETE", *args, **kwargs)

    async def options(self, *args: Any, **kwargs: Any) -> Response:
        return await self.request("OPTIONS", *args, **kwargs)

    async def patch(self, *args: Any, **kwargs: Any) -> Response:
        return await self.request("PATCH", *args, **kwargs)

    async def head(self, *args: Any, **kwargs: Any) -> Response:
        return await self.request("HEAD", *args, **kwargs)
