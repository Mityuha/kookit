import urllib.parse
from typing import Dict, Final, Iterable, List, Optional, Tuple, Union

from fastapi import APIRouter
from httpx import Request, Response
from typing_extensions import TypeGuard

from .handler import KookitHTTPHandler
from .interfaces import IKookitHTTPRequest, IKookitHTTPResponse
from .request_runner import KookitHTTPRequestRunner


def is_response(
    action: Union[IKookitHTTPResponse, IKookitHTTPRequest]
) -> TypeGuard[IKookitHTTPResponse]:
    return hasattr(action, "response") and isinstance(action.response, Response)


def is_request(
    action: Union[IKookitHTTPResponse, IKookitHTTPRequest]
) -> TypeGuard[IKookitHTTPRequest]:
    return (
        hasattr(action, "request")
        and isinstance(action.request, Request)
        and hasattr(action, "service")
    )


class KookitHTTPService:
    def __init__(
        self,
        url_env_var: Optional[str] = None,
        *,
        service_url: str = "",
        actions: Iterable[Union[IKookitHTTPRequest, IKookitHTTPResponse]] = (),
        service_name: str = "",
    ) -> None:
        self.url_env_var: Optional[str] = url_env_var
        self.router: Final[APIRouter] = APIRouter()
        self.method_url_2_handler: Final[Dict[Tuple[str, str], KookitHTTPHandler]] = {}
        self.initial_requests: Final[List[IKookitHTTPRequest]] = []
        self.service_url: str = service_url
        self.service_name: Final[str] = service_name or self.__class__.__name__
        self.add_actions(*actions)

    def __str__(self) -> str:
        return f"[{self.service_name}]"

    def add_actions(self, *actions: Union[IKookitHTTPResponse, IKookitHTTPRequest]) -> None:
        response_i: int = 0
        for response_i, action in enumerate(actions):
            if is_request(action):
                self.initial_requests.append(action)
            else:
                break

        handlers: List[KookitHTTPHandler] = []
        current_response: Optional[IKookitHTTPResponse] = None
        requests: List[IKookitHTTPRequest] = []

        actions = actions[response_i:]

        for action in actions:
            if is_response(action) and not requests:
                if current_response:
                    handlers.append(
                        KookitHTTPHandler(
                            current_response.response,
                            service_name=self.service_name,
                        )
                    )

                current_response = action
            elif is_response(action) and requests:
                assert current_response
                handlers.append(
                    KookitHTTPHandler(
                        current_response.response,
                        requests=requests,
                        service_name=self.service_name,
                    )
                )
                current_response = None
                requests.clear()
            elif is_request(action):
                requests.append(action)

        if current_response:
            handlers.append(
                KookitHTTPHandler(
                    current_response.response,
                    requests=requests,
                    service_name=self.service_name,
                )
            )
            current_response = None

        for handler in handlers:
            url, method = handler.url, handler.method
            try:
                self.method_url_2_handler[(method, url)].merge(handler)
            except KeyError:
                self.method_url_2_handler[(method, url)] = handler

        print(f"{self}: handlers {self.method_url_2_handler}")

        for (method, url), handler in self.method_url_2_handler.items():
            self.router.add_api_route(
                urllib.parse.urlparse(url).path,
                handler.__call__,
                methods=[method],
            )

    def clear_actions(self) -> None:
        print(f"{self}: clearing actions")
        self.method_url_2_handler.clear()

    def assert_completed(self) -> None:
        for handler in self.method_url_2_handler.values():
            handler.assert_completed()

    async def run(self) -> None:
        runner: KookitHTTPRequestRunner = KookitHTTPRequestRunner(
            self.initial_requests,
            service_name=self.service_name,
        )
        await runner.run_requests()
