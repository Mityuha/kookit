from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
import pytest
import requests  # type: ignore[import-untyped]

from kookit import Kookit, KookitJSONResponse


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
@pytest.mark.parametrize("client", [httpx, requests])
@pytest.mark.parametrize("what", ["headers", "content", "params"])
def test_request_matches_error(
    random_json_response: KookitJSONResponse,
    client: Any,
    kookit: Kookit,
    what: str,
    faker: Any,
) -> None:
    service = kookit.new_http_service(actions=[random_json_response])

    base_url: str = service.url
    request = random_json_response.request
    url: str = f"{base_url}{request.url}"

    headers = request.headers
    data = request.content
    params = parse_qs(urlparse(str(request.url)).query)

    if what == "headers":
        headers = faker.pydict(value_types=[str])
    elif what == "content":
        data = faker.json().encode()
        headers["Content-Length"] = str(len(data))  # type: ignore[index]
        what = "body"
    elif what == "params":
        params = faker.pydict(value_types=[str])

    with pytest.raises(RuntimeError), kookit:
        response = client.request(
            request.method,
            url,
            headers=headers,
            data=data,
            params=params,
        )

    assert response.status_code == 400
