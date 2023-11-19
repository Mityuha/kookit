from typing import Any

from httpx import Request

from kookit import KookitHTTPHandler


def test_http_handler_properties(mocker: Any, faker: Any) -> None:
    service_name: str = faker.pystr()
    url: str = f"{faker.uri_path()}/{{catalog_id}}"
    method: str = faker.pystr()
    response: Any = mocker.Mock(
        request=Request(
            url=url,
            method=method,
        )
    )

    handler = KookitHTTPHandler(response, service_name=service_name)

    assert handler.url == url
    assert handler.method == method.upper()
