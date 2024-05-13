from fastapi import APIRouter, Request
from multiprocess import Queue

from kookit import Kookit, KookitJSONRequest, KookitJSONResponse


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

    me = kookit.new_http_service(
        routers=[router],
        name="It's ME",
    )

    external_service = kookit.new_http_service(
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

    with kookit:
        response = kookit.put(external_service, random_uri_path)
        status_codes.put(response.status_code)

        await kookit.asleep(0.3)

    assert [status_codes.get(), status_codes.get(False)] == [random_status_code, 100]
