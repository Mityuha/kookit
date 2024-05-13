import pytest

from kookit import Kookit, KookitJSONResponse


@pytest.mark.xfail()
def test_request_not_found(
    random_method: str,
    random_status_code: int,
    random_headers: dict,
    random_uri_path: str,
    random_resp_json: dict,
    kookit: Kookit,
) -> None:
    kookit.new_http_service(
        actions=[
            KookitJSONResponse(
                random_resp_json,
                url=random_uri_path,
                method=random_method,
                status_code=random_status_code,
                headers=random_headers,
            )
        ],
        name="local_service",
    )

    with kookit:
        pass


@pytest.mark.skip(
    reason="There is no option to specify an external url for service for now. "
    "Would be added on demand"
)
def test_ignore_unused_responses_for_external_url(
    random_method: str,
    random_status_code: int,
    random_headers: dict,
    random_uri_path: str,
    random_resp_json: dict,
    kookit: Kookit,
) -> None:
    kookit.new_http_service(
        actions=[
            KookitJSONResponse(
                random_resp_json,
                url=random_uri_path,
                method=random_method,
                status_code=random_status_code,
                headers=random_headers,
            )
        ],
        name="external_service",
    )

    with kookit:
        ...
