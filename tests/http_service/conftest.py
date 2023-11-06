from random import choice
from typing import Any, Callable

import pytest

from kookit import KookitJSONResponse


@pytest.fixture
def random_method() -> str:
    return choice(["GET", "POST", "PUT", "DELETE", "PATCH"])


@pytest.fixture
def random_status_code() -> int:
    return choice([200, 201, 202, 400, 401, 403, 404, 409, 412, 422, 429, 500, 501, 502, 503, 504])


@pytest.fixture
def random_headers(faker: Any) -> dict:
    return faker.pydict(value_types=(str,))


@pytest.fixture
def random_resp_json(faker: Any) -> dict:
    return faker.pydict(value_types=(int, float, str))


@pytest.fixture
def random_uri_path(faker: Any) -> str:
    return f"/{faker.uri_path()}"


@pytest.fixture
def kookit_json_response_generator(faker: Any) -> Callable:
    def wrapper() -> KookitJSONResponse:
        return KookitJSONResponse(
            faker.pydict(value_types=(int, float, str)),
            url=f"/{faker.uri_path()}",
            method=choice(["GET", "POST", "PUT", "DELETE", "PATCH"]),
            status_code=choice(
                [200, 201, 202, 400, 401, 403, 404, 409, 412, 422, 429, 500, 501, 502, 503, 504]
            ),
            headers=faker.pydict(value_types=[str]),
            request_params=choice([faker.pydict(3, value_types=(str,)), faker.pystr()]),
            request_headers=faker.pydict(value_types=[str]),
            request_json=faker.pydict(value_types=[float, int, str]),
        )

    return wrapper


@pytest.fixture
def random_json_response(
    kookit_json_response_generator: Any,
) -> KookitJSONResponse:
    return kookit_json_response_generator()
