import os
from contextlib import asynccontextmanager
from multiprocessing import Value
from typing import Any, Final

import httpx
import pytest
from fastapi import APIRouter

from kookit import Kookit, KookitJSONResponse


router = APIRouter()
ROUTER_RESPONSE: Final = [{"username": "Rick"}, {"username": "Morty"}]


@router.get("/users")
async def read_users() -> list:
    return ROUTER_RESPONSE


class SimpleLifespan:
    def __init__(self) -> None:
        self.is_called = Value("i", 0)

    @asynccontextmanager
    async def __call__(self, _app: Any) -> Any:
        self.is_called.value = 1
        yield


@pytest.mark.parametrize("with_service", [True, False])
def test_single_service_response(
    random_method: str,
    random_status_code: int,
    faker: Any,
    kookit: Kookit,
    with_service: bool,
) -> None:
    kookit.show_logs()
    env_var: str = faker.pystr().upper()
    resp_json: dict = faker.pydict(value_types=(float, int, str))
    uri_path: str = f"/{faker.uri_path()}"
    headers: dict = faker.pydict(value_types=(str,))
    lifespans = [SimpleLifespan(), SimpleLifespan()]
    service = kookit.new_http_service(
        env_var,
        unique_url=True,
        actions=[
            KookitJSONResponse(
                resp_json,
                url=uri_path,
                method=random_method,
                status_code=random_status_code,
                headers=headers,
            )
        ],
        lifespans=lifespans,
        routers=[router],
    )
    assert os.environ[env_var] == service.url
    assert service.name == "service"

    cmanager: Any = service if with_service else kookit

    with cmanager:
        response = kookit.request(service, random_method, uri_path)
        router_response = httpx.get(f"{service.url}/users")

    assert response.status_code == random_status_code
    assert dict(response.headers).items() >= headers.items()
    assert response.json() == resp_json

    assert router_response.json() == ROUTER_RESPONSE
    assert all(lifespan.is_called for lifespan in lifespans)
