from enum import Enum
from typing import TYPE_CHECKING, Any

import pytest
import requests  # type: ignore[import-untyped]

from kookit import Kookit, KookitJSONResponse


if TYPE_CHECKING:
    from httpx import Response


class Request(Enum):
    REQUESTS_GEN = 1
    REQUESTS_METHOD = 2
    KOOKIT_GEN = 3
    KOOKIT_METHOD = 4


@pytest.mark.parametrize("use_request", Request)
def test_service_json_response(
    random_method: str,
    use_request: Request,
    random_status_code: int,
    faker: Any,
    kookit: Kookit,
) -> None:
    service = kookit.new_http_service()

    resp_json: dict = faker.pydict(value_types=(float, int, str))
    uri_path: str = f"/{faker.uri_path()}"
    headers: dict = faker.pydict(value_types=(str,))
    service = kookit.new_http_service(
        actions=[
            KookitJSONResponse(
                resp_json,
                url=uri_path,
                method=random_method,
                status_code=random_status_code,
                headers=headers,
            )
        ]
    )

    url: str = f"{service.url}{uri_path}"
    response: Response
    with kookit:
        if use_request == Request.REQUESTS_GEN:
            response = requests.request(random_method, url)
        elif use_request == Request.REQUESTS_METHOD:
            service_method = getattr(requests, random_method.lower())
            response = service_method(url)
        elif use_request == Request.KOOKIT_GEN:
            response = kookit.request(service, random_method, uri_path)
        else:
            method = getattr(kookit, random_method.lower())
            response = method(service, uri_path)

    assert response.status_code == random_status_code
    assert dict(response.headers).items() >= headers.items()
    assert response.json() == resp_json
