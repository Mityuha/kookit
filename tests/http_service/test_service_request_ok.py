import json

from kookit import Kookit, KookitHTTPService, KookitJSONRequest, KookitJSONResponse


async def test_service_callback_to_yourself(
    random_json_response: KookitJSONResponse,
    kookit: Kookit,
) -> None:
    service = KookitHTTPService()

    request = random_json_response.response.request

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

    await kookit.prepare_services(service)
    await kookit.start_services()
