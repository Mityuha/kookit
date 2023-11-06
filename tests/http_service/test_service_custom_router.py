from typing import Any, Final

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from httpx import Response

from kookit import Kookit, KookitHTTPService


class CustomRouter:
    def __init__(
        self, method: str, url: str, *, status_code: int, json: Any, headers: dict
    ) -> None:
        self.router: Final[APIRouter] = APIRouter()
        self.router.add_api_route(url, self.__call__, methods=[method])
        self.status_code: Final[int] = status_code
        self.json: Final[Any] = json
        self.headers: Final[dict] = headers

    async def __call__(self, request: Request) -> JSONResponse:
        return JSONResponse(
            self.json,
            status_code=self.status_code,
            headers=self.headers,
        )


async def test_service_json_response(
    random_method: str,
    random_status_code: int,
    random_resp_json: dict,
    random_headers: dict,
    random_uri_path: str,
    kookit: Kookit,
) -> None:
    service = KookitHTTPService(
        routers=[
            CustomRouter(
                method=random_method,
                url=random_uri_path,
                status_code=random_status_code,
                json=random_resp_json,
                headers=random_headers,
            ).router
        ]
    )

    await kookit.prepare_services(service)
    await kookit.start_services()

    for _ in range(5):
        method = getattr(kookit, random_method.lower())
        response: Response = await method(service, random_uri_path)

        assert response.status_code == random_status_code
        assert dict(response.headers).items() >= random_headers.items()
        assert response.json() == random_resp_json
