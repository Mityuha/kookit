import json

from kookit import Kookit, KookitJSONRequest, KookitJSONResponse


def test_service_callback_to_yourself(
    random_json_response: KookitJSONResponse,
    kookit: Kookit,
) -> None:
    service = kookit.new_http_service()

    request = random_json_response.request

    service.add_actions(
        KookitJSONRequest(
            service,
            method=request.method,
            url=request.url,
            headers=request.headers,
            json=json.loads(request.content),
        ),
        random_json_response,
    )

    with kookit:
        pass
