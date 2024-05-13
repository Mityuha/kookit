import json
from typing import Any

import httpx
import pytest
import requests  # type: ignore[import-untyped]

from kookit import Kookit, KookitJSONResponse


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("client", [httpx, requests])
def test_request_matches_ok(
    random_json_response: KookitJSONResponse,
    client: Any,
    kookit: Kookit,
) -> None:
    service = kookit.new_http_service(actions=[random_json_response])

    base_url: str = service.url
    request = random_json_response.request
    url: str = f"{base_url}{request.url}"

    with kookit:
        response = client.request(
            request.method,
            url,
            headers=request.headers,
            data=request.content,
        )

    assert response.status_code == random_json_response.status_code
    assert response.json() == json.loads(random_json_response.content)
