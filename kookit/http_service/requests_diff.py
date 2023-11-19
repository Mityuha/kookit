from typing import Any, Mapping, Optional, Protocol

from httpx import URL


class ExpectedRequest(Protocol):
    @property
    def content(self) -> bytes:
        ...

    @property
    def headers(self) -> Optional[Mapping[str, str]]:
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

    if request.headers and not all(
        it in frequest.headers.items() for it in request.headers.items()
    ):
        return f"Expected headers present: {dict(request.headers)}, got: {dict(frequest.headers)}"

    assert request.url.path.format(**frequest.path_params) == frequest.url.path

    if request.url.query and request.url.query.decode("ascii") != frequest.url.query:
        return f"Expected query params: '{request.url.query!r}', got: '{frequest.url.query}'"

    return ""
