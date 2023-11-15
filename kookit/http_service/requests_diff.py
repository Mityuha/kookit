from typing import Any, Mapping, MutableMapping, Optional, Protocol
from urllib.parse import parse_qs

from httpx import URL


class ExpectedRequest(Protocol):
    @property
    def content(self) -> bytes:
        ...

    @property
    def headers(self) -> Optional[MutableMapping[str, str]]:
        ...

    @property
    def url(self) -> URL:
        ...


class RequestGot(Protocol):
    async def body(self) -> bytes:
        ...

    @property
    def headers(self) -> Mapping[str, str]:
        ...

    @property
    def url(self) -> Any:
        ...

    @property
    def path_params(self) -> dict:
        ...


async def compare_requests(
    frequest: RequestGot,
    request: ExpectedRequest,
) -> str:
    content = request.content
    fcontent = await frequest.body()
    if content and content != fcontent:
        return f"Expected body: '{content!r}', got: '{fcontent!r}'"

    # TODO. Maybe, class other than Request required
    # see tests/http_service/test_diff_headers_and_path_template_response.py
    if request.headers and not all(
        it in frequest.headers.items() for it in request.headers.items()
    ):
        return f"Expected headers present: {dict(request.headers)}, got: {dict(frequest.headers)}"

    # TODO: Need to check path without params
    # see tests/http_service/test_diff_headers_and_path_template_response.py
    # Because /catalog/{id} != /catalog/2
    assert request.url.path.format(**frequest.path_params) == frequest.url.path

    if request.url.query and parse_qs(request.url.query) != frequest.url.query:
        return f"Expected query params: '{request.url.query!r}', got: '{frequest.url.query}'"

    return ""
