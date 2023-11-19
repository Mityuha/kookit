from fastapi import APIRouter, Request
from multiprocess import Queue

from kookit import Kookit, KookitHTTPService, KookitJSONRequest, KookitJSONResponse


async def test_response_got_before_request(
    random_status_code: int,
    random_headers: dict,
    random_uri_path: str,
    random_resp_json: dict,
    kookit: Kookit,
) -> None:
    status_codes: Queue = Queue()

    router: APIRouter = APIRouter()

    @router.get("/test/request")
    async def test_endpoint(request: Request) -> None:
        assert await request.json() == {}
        status_codes.put(100)

    me = KookitHTTPService(routers=[router], service_name="It's ME")

    external_service = KookitHTTPService(
        actions=[
            KookitJSONResponse(
                random_resp_json,
                url=random_uri_path,
                method="PUT",
                status_code=random_status_code,
                headers=random_headers,
            ),
            KookitJSONRequest(
                me,
                json={},
                url="/test/request",
                method="GET",
                request_delay=0.2,
            ),
        ]
    )

    await kookit.prepare_services(external_service, me)
    await kookit.start_services()

    response = await kookit.put(external_service, random_uri_path)
    status_codes.put(response.status_code)

    await kookit.wait(0.3)

    assert [status_codes.get(), status_codes.get(False)] == [random_status_code, 100]
