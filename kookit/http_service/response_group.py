import time
from collections.abc import Mapping
from typing import Any, Final

from httpx import URL, Client

from kookit.logging import logger
from ..http_models import KookitHTTPRequest, KookitHTTPResponse
from .interfaces import IRequest


class ResponseGroup:
    def __init__(
        self,
        response: KookitHTTPResponse | None = None,
        parent: Any = "",
    ) -> None:
        self._parent: Final = parent
        self._response: Final = response
        self._requests: list[KookitHTTPRequest] = []
        self._active: bool = True

    @property
    def active(self) -> bool:
        return self._active

    def __str__(self) -> str:
        return f"<ResponseGroup([{self._parent}], '{self.method}', '{self.url}'>"

    def add_requests(self, *requests: KookitHTTPRequest) -> None:
        self._requests.extend(requests)

    @property
    def response(self) -> KookitHTTPResponse | None:
        return self._response

    @property
    def url(self) -> URL | None:
        if not self.response:
            return None
        return self.response.request.url

    @property
    def method(self) -> str:
        if not self.response:
            return ""
        return self.response.request.method

    @property
    def path(self) -> str:
        if not self.response:
            return ""
        return self.response.request.url.path

    @property
    def query(self) -> bytes:
        if not self.response:
            return b""
        return self.response.request.url.query

    @property
    def content(self) -> bytes:
        if not self.response:
            return b""
        return self.response.request.content

    @property
    def headers(self) -> Mapping[str, str]:
        if not self.response:
            return {}
        return self.response.request.headers or {}

    def __eq__(self, request: IRequest) -> bool:  # type: ignore
        if not self.response or not self.active:
            return False

        if self.method != request.method:
            logger.trace(f"{self}: expected method: {self.method}, got: {request.method}")
            return False

        try:
            expected_url_path = self.path.format(**request.path_params)
        except KeyError:
            logger.trace(
                f"{self}: Incomparable url path. Expected url path: {self.path}, got: {request.url.path}"
            )
            return False

        if expected_url_path != request.url.path:
            logger.trace(
                f"{self}: Expected url path: {expected_url_path}, got: {request.url.path}"
            )
            return False

        if self.content != request.content:
            logger.trace(f"{self}: Expected body: '{self.content!r}', got: '{request.content!r}'")
            return False

        if self.headers and not all(it in request.headers.items() for it in self.headers.items()):
            logger.trace(
                f"{self}: Expected headers: {dict(self.headers)}, got: {dict(request.headers)}"
            )
            return False

        if self.query and self.query.decode("ascii") != request.url.query:
            logger.trace(
                f"{self}: Expected query params: '{self.query!r}', got: '{request.url.query!r}'"
            )
            return False
        return True

    def __enter__(self) -> "ResponseGroup":
        return self

    def __exit__(self, *_args: Any) -> None:
        logger.trace(f"{self}: running {len(self._requests)} requests")
        for req in self._requests:
            logger.debug(
                f"{self}: running request <{req.method} {req.url}> ({req.service.url=}, {req.request_delay=}))"
            )
            time.sleep(req.request_delay)
            with Client(base_url=req.service.url) as client:
                response = client.request(
                    method=req.method,
                    url=req.url,
                    content=req.content,
                    headers=req.headers,
                    timeout=60,
                )

                logger.trace(
                    f"{self}: request <{req.method} {req.url}> successfully executed: {response}"
                )
        self._active = False
