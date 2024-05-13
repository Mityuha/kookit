from typing import Any

import httpx
import pytest
import requests  # type: ignore[import-untyped]

from kookit import Kookit, KookitJSONResponse


@pytest.mark.parametrize("client", [httpx, requests])
def test_extra_response_error(
    random_method: str,
    random_status_code: int,
    random_headers: dict,
    random_uri_path: str,
    random_resp_json: dict,
    client: Any,
    kookit: Kookit,
) -> None:
    service = kookit.new_http_service(
        actions=[
            KookitJSONResponse(
                random_resp_json,
                url=random_uri_path,
                method=random_method,
                status_code=random_status_code,
                headers=random_headers,
            )
        ]
    )

    base_url: str = service.url
    url: str = f"{base_url}{random_uri_path}"

    with kookit:
        response = client.request(random_method, url)
        error_response = client.request(random_method, url)

    assert response.status_code == random_status_code, response.json()
    assert dict(response.headers).items() >= random_headers.items()
    assert response.json() == random_resp_json
    assert error_response.status_code == 400
    assert error_response.json()
