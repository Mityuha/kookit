from typing import Protocol

from httpx import Request, Response


class IKookitHTTPResponse(Protocol):
    @property
    def response(self) -> Response:
        ...


class IKookitService(Protocol):
    @property
    def service_url(self) -> str:
        ...


class IKookitHTTPRequest(Protocol):
    @property
    def request(self) -> Request:
        ...

    @property
    def service(self) -> IKookitService:
        ...
