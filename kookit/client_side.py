from typing import Any, Protocol

from httpx import Client, Response


class IKookitService(Protocol):
    @property
    def url(self) -> str: ...


class KookitHTTPClient:
    def request(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        with Client(base_url=service.url) as client:
            return client.request(*args, **kwargs)

    def get(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return self.request(service, "GET", *args, **kwargs)

    def post(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return self.request(service, "POST", *args, **kwargs)

    def put(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return self.request(service, "PUT", *args, **kwargs)

    def delete(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return self.request(service, "DELETE", *args, **kwargs)

    def options(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return self.request(service, "OPTIONS", *args, **kwargs)

    def patch(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return self.request(service, "PATCH", *args, **kwargs)

    def head(self, service: IKookitService, *args: Any, **kwargs: Any) -> Response:
        return self.request(service, "HEAD", *args, **kwargs)
