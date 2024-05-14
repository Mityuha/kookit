from contextlib import asynccontextmanager
from typing import Any, Final

import httpx
from fastapi import APIRouter

from kookit import Kookit


router = APIRouter()
ROUTER_RESPONSE: Final = [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users")
async def read_users() -> list:
    return ROUTER_RESPONSE


def test_add_router_inside_lifespan(
    faker: Any,
    kookit: Kookit,
) -> None:
    kookit.show_logs()
    faker.pydict(value_types=(float, int, str))
    f"/{faker.uri_path()}"
    faker.pydict(value_types=(str,))
    service = kookit.new_http_service()

    @asynccontextmanager
    async def lifespan(_app: Any) -> Any:
        service.add_routers(router)
        yield

    service.add_lifespans(lifespan)

    with service, kookit:
        kookit_response = kookit.get(service, "/users")
        response = httpx.get(f"{service.url}/users")

    assert kookit_response.json() == response.json() == ROUTER_RESPONSE
