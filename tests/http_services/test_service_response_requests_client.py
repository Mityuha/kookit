from typing import Any

import pytest
import requests  # type: ignore
from httpx import Response

from kookit import Kookit, KookitHTTPService, KookitJSONResponse


@pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE"])
@pytest.mark.parametrize("use_request", [True, False])
@pytest.mark.parametrize("status_code", [200, 503])
async def test_service_json_response(
    method: str,
    use_request: bool,
    status_code: int,
    faker: Any,
    kookit: Kookit,
) -> None:
    service = KookitHTTPService()

    resp_json: dict = faker.pydict(value_types=(float, int, str))
    uri_path: str = f"/{faker.uri_path()}"
    headers: dict = faker.pydict(value_types=(str,))
    service.add_actions(
        KookitJSONResponse(
            resp_json,
            url=uri_path,
            method=method,
            status_code=status_code,
            headers=headers,
        )
    )

    kookit.prepare_services(service)
    await kookit.start_services()

    base_url: str = service.service_url
    url: str = f"{base_url}{uri_path}"

    response: Response
    if use_request:
        response = requests.request(method, url)
    else:
        service_method = getattr(requests, method.lower())
        response = service_method(url)

    assert response.status_code == status_code
    assert dict(response.headers).items() >= headers.items()
    assert response.json() == resp_json
