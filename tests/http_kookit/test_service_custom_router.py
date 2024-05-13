from typing import TYPE_CHECKING, Any, Final

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from kookit import Kookit


if TYPE_CHECKING:
    from httpx import Response


class CustomRouter:
    def __init__(
        self, method: str, url: str, *, status_code: int, json: Any, headers: dict
    ) -> None:
        self.router: Final[APIRouter] = APIRouter()
        self.router.add_api_route(url, self.__call__, methods=[method])
        self.status_code: Final[int] = status_code
        self.json: Final[Any] = json
        self.headers: Final[dict] = headers

    # ruff: noqa: ARG002
    async def __call__(self, request: Request) -> JSONResponse:
        return JSONResponse(
            self.json,
            status_code=self.status_code,
            headers=self.headers,
        )


def test_service_json_response(
    random_method: str,
    random_status_code: int,
    random_resp_json: dict,
    random_headers: dict,
    random_uri_path: str,
    kookit: Kookit,
) -> None:
    service = kookit.new_http_service(
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

    with kookit:
        for _ in range(5):
            method = getattr(kookit, random_method.lower())
            response: Response = method(service, random_uri_path)

            assert response.status_code == random_status_code
            assert dict(response.headers).items() >= random_headers.items()
            assert response.json() == random_resp_json
