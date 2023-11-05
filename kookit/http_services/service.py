from typing import Final, List, Optional, Set, Tuple, Union

from fastapi import APIRouter
from fastapi import Request as FastAPIRequest
from fastapi import Response as FastAPIResponse

from ..http_responses import KookitHTTPCallback, KookitHTTPResponse
from .client_side import KookitHTTPClientSide
from .handler import KookitHTTPCallbackRunner, KookitHTTPHandler


class KookitHTTPService(KookitHTTPClientSide):
    def __init__(
        self,
        url_env_var: Optional[str] = None,
        *,
        service_url: str = "",
    ) -> None:
        self.url_env_var: Optional[str] = url_env_var
        self.router: Final[APIRouter] = APIRouter()
        self.ordered_handlers: List[KookitHTTPHandler] = []
        self.current_handler: int = 0
        self.initial_callbacks: Final[List[KookitHTTPCallback]] = []
        self._service_url: str = service_url
        super().__init__(self.router)

    @property
    def service_url(self) -> str:
        return self._service_url

    @service_url.setter
    def service_url(self, new_service_url: str) -> None:
        self._service_url = new_service_url

    def ordered_actions(self, *actions: Union[KookitHTTPResponse, KookitHTTPCallback]) -> None:
        response_i: int = 0
        for response_i, action in enumerate(actions):
            if isinstance(action, KookitHTTPCallback):
                self.initial_callbacks.append(action)
            else:
                break

        handlers: List[KookitHTTPHandler] = []
        current_response: Optional[KookitHTTPResponse] = None
        callbacks: List[KookitHTTPCallback] = []

        actions = actions[response_i:]

        for action in actions:
            if isinstance(action, KookitHTTPResponse) and not callbacks:
                if current_response:
                    handlers.append(KookitHTTPHandler(current_response.response))
                    current_response = None
                else:
                    current_response = action
            elif isinstance(action, KookitHTTPResponse) and callbacks:
                assert current_response
                handlers.append(
                    KookitHTTPHandler(
                        current_response.response,
                        callbacks=callbacks,
                    )
                )
                current_response = None
                callbacks.clear()
            elif isinstance(action, KookitHTTPCallback):
                callbacks.append(action)

        if current_response:
            handlers.append(
                KookitHTTPHandler(
                    current_response.response,
                    callbacks=callbacks,
                )
            )
            current_response = None

        unique_urls: Set[Tuple[str, str]] = set()
        for h in handlers:
            url, method = h.r.request.url, h.r.request.method
            if (method, url) in unique_urls:
                continue
            self.router.add_api_route(
                str(url),
                self.__call__,
                methods=[method],
            )
            unique_urls.add((method, str(url)))

        self.ordered_handlers += handlers

    async def __call__(self, request: FastAPIRequest) -> FastAPIResponse:
        handler: KookitHTTPHandler = self.ordered_handlers[self.current_handler]
        self.current_handler += 1
        response: FastAPIResponse = handler.response
        await handler.run_callbacks()
        return response

    async def run(self) -> None:
        runner: KookitHTTPCallbackRunner = KookitHTTPCallbackRunner(self.initial_callbacks)
        await runner.run_callbacks()
