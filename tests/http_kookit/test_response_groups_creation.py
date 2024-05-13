from typing import Any

from kookit.http_kookit.service import KookitHTTPRequest, KookitHTTPResponse, KookitHTTPService


def test_response_groups(faker: Any) -> None:
    def request() -> KookitHTTPRequest:
        return KookitHTTPRequest(None, url="/", method="GET")  # type: ignore[arg-type]

    def response() -> KookitHTTPResponse:
        return KookitHTTPResponse("/url", "GET")

    actions = [
        faker.random_element([request(), response()]) for _ in range(faker.pyint(max_value=100))
    ]

    groups = KookitHTTPService.create_response_groups(actions)

    assert len(groups) == len([1 for a in actions if isinstance(a, KookitHTTPResponse)])
