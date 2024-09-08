from typing import Any

import pytest

from kookit import Kookit, KookitJSONResponse


@pytest.mark.parametrize("method", ["POST", "PUT"])
def test_request_content_does_not_match(faker: Any, kookit: Kookit, method: str) -> None:
    service = kookit.new_http_service()

    uri_path: str = f"/{faker.uri_path()}"
    service.add_actions(
        KookitJSONResponse(
            faker.pydict(value_types=[str]),
            url=uri_path,
            method=method,
            request_json=None,
        )
    )

    url: str = f"{service.url}{uri_path}"
    with pytest.raises(RuntimeError), kookit:  # noqa: PT012
        method_call = getattr(kookit, method.lower())
        method_call(
            service,
            url,
            json=faker.pydict(value_types=(float, int, str)),
        )
