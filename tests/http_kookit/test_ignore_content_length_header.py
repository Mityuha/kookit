from typing import Any

import pytest

from kookit import Kookit, KookitJSONResponse


@pytest.mark.parametrize("method", ["POST", "PUT"])
def test_ignore_content_length_header(
    random_status_code: int, faker: Any, kookit: Kookit, method: str
) -> None:
    service = kookit.new_http_service()

    resp_json: dict = faker.pydict(value_types=(float, int, str))
    uri_path: str = f"/{faker.uri_path()}"
    headers: dict = faker.pydict(value_types=(str,))
    service.add_actions(
        KookitJSONResponse(
            resp_json,
            url=uri_path,
            method=method,
            status_code=random_status_code,
            request_headers=headers,
        )
    )

    url: str = f"{service.url}{uri_path}"
    with kookit:
        method_call = getattr(kookit, method.lower())
        response = method_call(
            service,
            url,
            headers=headers,
            json=faker.pydict(value_types=(float, int, str)),
        )

    assert response.json() == resp_json


@pytest.mark.parametrize("method", ["POST", "PUT"])
@pytest.mark.parametrize("payload_specified", [True, False])
def test_zero_content_length_header_as_expected(
    random_status_code: int,
    faker: Any,
    kookit: Kookit,
    method: str,
    payload_specified: bool,
) -> None:
    service = kookit.new_http_service()

    resp_json: dict = faker.pydict(value_types=(float, int, str))
    uri_path: str = f"/{faker.uri_path()}"
    headers: dict = faker.pydict(value_types=(str,))
    service.add_actions(
        KookitJSONResponse(
            resp_json,
            url=uri_path,
            method=method,
            status_code=random_status_code,
            request_headers=headers,
            request_json=None,
        )
    )

    url: str = f"{service.url}{uri_path}"
    payload: dict = {"json": None} if payload_specified else {}
    with kookit:
        method_call = getattr(kookit, method.lower())
        response = method_call(
            service,
            url,
            headers=headers,
            **payload,
        )

    assert response.json() == resp_json
