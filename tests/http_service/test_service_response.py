from typing import Any

import pytest
from httpx import Response

from kookit import Kookit, KookitHTTPService, KookitJSONResponse


@pytest.mark.parametrize("use_request", [True, False])
async def test_service_json_response(
    random_method: str,
    use_request: bool,
    random_status_code: int,
    faker: Any,
    kookit: Kookit,
) -> None:
    service = KookitHTTPService()

    resp_json: dict = faker.pydict(value_types=(float, int, str))
    uri_path: str = f"/{faker.uri_path()}"
    headers: dict = faker.pydict(value_types=(str,))
    service = KookitHTTPService(
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

    await kookit.prepare_services(service)
    await kookit.start_services()

    response: Response
    if use_request:
        response = await kookit.request(service, random_method, uri_path)
    else:
        method = getattr(kookit, random_method.lower())
        response = await method(service, uri_path)

    assert response.status_code == random_status_code
    assert dict(response.headers).items() >= headers.items()
    assert response.json() == resp_json
