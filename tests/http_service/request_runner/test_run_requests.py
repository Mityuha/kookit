from typing import Any, List

from httpx import Response

from kookit import KookitHTTPRequestRunner, KookitJSONRequest


async def test_run_requests(
    httpx_mock: Any,
    random_json_request: KookitJSONRequest,
    faker: Any,
) -> None:
    runner = KookitHTTPRequestRunner(
        [random_json_request],
        service_name="",
    )

    r = random_json_request
    status_code: int = 205
    json_resp: dict = faker.pydict(value_types=[int, float, str])
    httpx_mock.add_response(
        url=f"{random_json_request.service.service_url}{r.url}",
        method=r.method,
        status_code=status_code,
        match_content=r.content,
        match_headers=r.headers,
        json=json_resp,
    )

    responses: List[Response] = await runner.run_requests()

    assert len(responses) == 1
    resp = responses[0]
    assert resp.status_code == status_code
    assert resp.json() == json_resp
