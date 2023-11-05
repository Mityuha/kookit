from typing import Any

import httpx
import pytest
import requests  # type: ignore
from httpx import Request

from kookit import Kookit, KookitHTTPService, KookitJSONResponse


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("client", [httpx, requests])
async def test_request_matches_ok(
    random_json_response: KookitJSONResponse,
    client: Any,
    kookit: Kookit,
    faker: Any,
) -> None:
    service = KookitHTTPService()

    service.add_actions(
        random_json_response,
    )

    kookit.prepare_services(service)
    await kookit.start_services()

    base_url: str = service.service_url
    request: Request = random_json_response.response.request
    url: str = f"{base_url}{request.url}"

    response = client.request(
        request.method,
        url,
        headers=request.headers,
        data=request.content,
    )

    assert response.status_code == random_json_response.response.status_code
    assert response.json() == random_json_response.response.json()
