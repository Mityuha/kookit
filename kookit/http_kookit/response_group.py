from __future__ import annotations
import time
from typing import TYPE_CHECKING, Any, Final

from httpx import URL, Client
from multiprocess import Value
from typing_extensions import Self

from kookit.logging import logger


if TYPE_CHECKING:
    from .interfaces import IRequest
    from .models import KookitHTTPRequest, KookitHTTPResponse


class ResponseGroup:
    def __init__(
        self,
        response: KookitHTTPResponse | None = None,
        parent: Any = "",
    ) -> None:
        self._parent: Final = parent
        self._response: Final = response
        self._requests: list[KookitHTTPRequest] = []
        self._active: Value = Value("i", 1)

    @property
    def active(self) -> bool:
        return bool(self._active.value)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"<ResponseGroup({self._parent}, '{self.method}', '{self.url}'>"

    def add_requests(self, *requests: KookitHTTPRequest) -> None:
        self._requests.extend(requests)

    @property
    def response(self) -> KookitHTTPResponse | None:
        return self._response

    @property
    def request(self) -> Any | None:
        if not self._response:
            return None
        return self._response.request

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

    # ruff: noqa: PLR0911
    def __eq__(self, request: IRequest) -> bool:  # type: ignore[override]
        if not self.response or not self.active:
            return False

        if self.method != request.method:
            logger.trace(f"{self}: expected method: {self.method}, got: {request.method}")
            return False

        try:
            expected_url_path = self.path.format(**request.path_params)
        except KeyError:
            logger.trace(
                f"{self}: Incomparable url path. Expected url path: {self.path}, "
                f"got: {request.url.path}",
            )
            return False

        if expected_url_path != request.url.path:
            logger.trace(
                f"{self}: Expected url path: {expected_url_path}, got: {request.url.path}",
            )
            return False

        req = self.response.request

        if req.content and req.content != request.content:
            logger.trace(f"{self}: Expected body: '{req.content!r}', got: '{request.content!r}'")
            return False

        if req.headers and not all(it in request.headers.items() for it in req.headers.items()):
            logger.trace(
                f"{self}: Expected headers: {dict(req.headers)}, got: {dict(request.headers)}",
            )
            return False

        if self.query and self.query.decode("ascii") != request.url.query:
            logger.trace(
                f"{self}: Expected query params: '{self.query!r}', got: '{request.url.query!r}'",
            )
            return False

        logger.trace(f"{self}: request {request} matched")
        return True

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        logger.trace(f"{self}: running {len(self._requests)} requests")
        for req in self._requests:
            logger.debug(
                f"{self}: running request <{req.method} {req.url}> ({req.service.url=}, "
                f"{req.request_delay=}))",
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
                    f"{self}: request <{req.method} {req.url}> "
                    f"successfully executed ==> {response}",
                )

        with self._active.get_lock():
            self._active.value = 0
