from urllib.parse import parse_qs, urlparse

from fastapi import Request as FastAPIRequest
from httpx import Request


async def compare_requests(
    frequest: FastAPIRequest,
    request: Request,
) -> str:
    content = request.content
    fcontent = await frequest.body()
    if content != fcontent:
        return f"Expected body: '{content!r}', got: '{fcontent!r}'"

    if not all(it in frequest.headers.items() for it in request.headers.items()):
        return f"Expected headers present: {dict(request.headers)}, got: {dict(frequest.headers)}"

    parsed_url = urlparse(str(request.url))
    parsed_furl = urlparse(str(frequest.url))

    assert parsed_url.path == parsed_furl.path

    if parsed_url.query and parse_qs(parsed_url.query) != parse_qs(parsed_furl.query):
        return f"Expected query params: '{parsed_url.query}', got: '{parsed_furl.query}'"

    return ""
