import pytest

from kookit import Kookit, KookitHTTPService, KookitJSONResponse


@pytest.mark.xfail
async def test_request_not_found(
    random_method: str,
    random_status_code: int,
    random_headers: dict,
    random_uri_path: str,
    random_resp_json: dict,
    kookit: Kookit,
) -> None:
    service = KookitHTTPService(
        actions=[
            KookitJSONResponse(
                random_resp_json,
                url=random_uri_path,
                method=random_method,
                status_code=random_status_code,
                headers=random_headers,
            )
        ],
        service_name="local_service",
    )

    await kookit.prepare_services(service)
    await kookit.start_services()

    await kookit.stop_services()


async def test_ignore_unused_responses_for_external_url(
    random_method: str,
    random_status_code: int,
    random_headers: dict,
    random_uri_path: str,
    random_resp_json: dict,
    kookit: Kookit,
) -> None:
    service = KookitHTTPService(
        actions=[
            KookitJSONResponse(
                random_resp_json,
                url=random_uri_path,
                method=random_method,
                status_code=random_status_code,
                headers=random_headers,
            )
        ],
        service_name="external_service",
    )
    service.service_url = "https://some.external_url:9801"

    await kookit.prepare_services(service)
    await kookit.start_services()

    await kookit.stop_services()
