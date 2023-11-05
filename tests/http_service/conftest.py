from random import choice
from typing import Any

import pytest


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
