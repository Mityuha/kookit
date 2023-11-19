from typing import Mapping, Optional, Protocol, runtime_checkable

from httpx import URL


@runtime_checkable
class IRequest(Protocol):
    @property
    def content(self) -> bytes:
        ...

    @property
    def headers(self) -> Optional[Mapping[str, str]]:
        ...

    @property
    def url(self) -> URL:
        ...

    @property
    def method(self) -> str:
        ...


@runtime_checkable
class IKookitHTTPResponse(Protocol):
    @property
    def request(self) -> IRequest:
        ...

    @property
    def content(self) -> bytes:
        ...

    @property
    def headers(self) -> Mapping[str, str]:
        ...

    @property
    def status_code(self) -> int:
        ...


class IKookitService(Protocol):
    @property
    def service_url(self) -> str:
        ...


@runtime_checkable
class IKookitHTTPRequest(Protocol):
    @property
    def content(self) -> bytes:
        ...

    @property
    def headers(self) -> Mapping[str, str]:
        ...

    @property
    def url(self) -> URL:
        ...

    @property
    def method(self) -> str:
        ...

    @property
    def service(self) -> IKookitService:
        ...

    @property
    def request_delay(self) -> float:
        ...
