from typing import Any

import httpx
import pytest
import requests  # type: ignore

from kookit import Kookit, KookitHTTPService, KookitJSONResponse


@pytest.mark.parametrize("client", [httpx, requests])
async def test_request_not_found(
    random_method: str,
    random_status_code: int,
    random_headers: dict,
    random_uri_path: str,
    random_resp_json: dict,
    client: Any,
    kookit: Kookit,
    faker: Any,
) -> None:
    service = KookitHTTPService(
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

    await kookit.prepare_services(service)
    await kookit.start_services()

    base_url: str = service.service_url
    url: str = f"{base_url}/{faker.uri_path()}"

    response = client.request(random_method, url)

    assert response.status_code == 404
    assert response.json()

    service.clear_actions()
