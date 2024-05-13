from typing import Any

import httpx
import pytest
import requests  # type: ignore[import-untyped]

from kookit import Kookit, KookitJSONResponse


@pytest.mark.parametrize("client", [httpx, requests])
def test_handlers_merge_ok(
    random_method: str,
    random_status_code: int,
    random_headers: dict,
    random_uri_path: str,
    random_resp_json: dict,
    client: Any,
    kookit: Kookit,
    faker: Any,
) -> None:
    random_resp_json2: dict = faker.pydict(value_types=(str,))
    random_status_code2: int = 507
    random_headers2: dict = faker.pydict(value_types=(str,))
    service = kookit.new_http_service(
        actions=[
            KookitJSONResponse(
                random_resp_json,
                url=random_uri_path,
                method=random_method,
                status_code=random_status_code,
                headers=random_headers,
            ),
            KookitJSONResponse(
                random_resp_json2,
                url=random_uri_path,
                method=random_method,
                status_code=random_status_code2,
                headers=random_headers2,
            ),
        ]
    )

    base_url: str = service.url
    url: str = f"{base_url}{random_uri_path}"

    with kookit:
        for status_code, headers, resp_json in [
            (random_status_code, random_headers, random_resp_json),
            (random_status_code2, random_headers2, random_resp_json2),
        ]:
            response = client.request(random_method, url)

            assert response.status_code == status_code, response.json()
            assert dict(response.headers).items() >= headers.items()
            assert response.json() == resp_json
