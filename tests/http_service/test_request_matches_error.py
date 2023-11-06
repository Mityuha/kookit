from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import requests  # type: ignore
from httpx import Request

from kookit import Kookit, KookitHTTPService, KookitJSONResponse


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("client", [httpx, requests])
@pytest.mark.parametrize("what", ["headers", "content", "params"])
async def test_request_matches_error(
    random_json_response: KookitJSONResponse,
    client: Any,
    kookit: Kookit,
    what: str,
    faker: Any,
) -> None:
    service = KookitHTTPService(actions=[random_json_response])

    await kookit.prepare_services(service)
    await kookit.start_services()

    base_url: str = service.service_url
    request: Request = random_json_response.response.request
    url: str = f"{base_url}{request.url}"

    headers = request.headers
    data = request.content
    params = parse_qs(urlparse(str(request.url)).query)

    if what == "headers":
        headers = faker.pydict(value_types=[str])
    elif what == "content":
        data = faker.json().encode()
        headers["Content-Length"] = str(len(data))
        what = "body"
    elif what == "params":
        params = faker.pydict(value_types=[str])

    response = client.request(request.method, url, headers=headers, data=data, params=params)

    assert response.status_code == 400
    assert what in response.json()["error"]

    service.clear_actions()
