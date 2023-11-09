import asyncio
from typing import Any

import pytest
from httpx import Request

from kookit import KookitHTTPRequestRunner, KookitJSONRequest


async def test_run_requests(
    httpx_mock: Any,
    random_json_request: KookitJSONRequest,
) -> None:
    runner = KookitHTTPRequestRunner(
        [random_json_request],
        service_name="",
    )

    r: Request = random_json_request.request
    httpx_mock.add_response(
        url=f"{random_json_request.service.service_url}{r.url}",
        method=r.method,
        match_content=r.content,
        match_headers=r.headers,
    )

    random_json_request.request_delay = 0.5  # type: ignore
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(runner.run_requests(), 0.3)

    random_json_request.request_delay = 0.0  # type: ignore
    await asyncio.wait_for(runner.run_requests(), 0.1)
