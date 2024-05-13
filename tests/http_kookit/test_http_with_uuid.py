from typing import Any

from kookit import Kookit, KookitJSONRequest, KookitJSONResponse


def test_uuid_type(
    faker: Any,
    random_method: str,
    random_uri_path: str,
    random_headers: dict,
    kookit: Kookit,
) -> None:
    service = kookit.new_http_service()

    request_json: dict = {
        faker.pystr(): faker.uuid4(None),
        faker.pystr(): faker.pyfloat(),
        faker.pystr(): faker.pystr(),
    }

    response_json: dict = {
        faker.pystr(): faker.uuid4(None),
        faker.pystr(): faker.pyfloat(),
        faker.pystr(): faker.pystr(),
    }

    service.add_actions(
        KookitJSONRequest(
            service,
            method=random_method,
            url=random_uri_path,
            headers=random_headers,
            json=request_json,
        ),
        KookitJSONResponse(
            response_json,
            method=random_method,
            url=random_uri_path,
            request_headers=random_headers,
            request_json=request_json,
        ),
    )

    with kookit:
        pass
