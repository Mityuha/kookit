from typing import Dict, Final, List, Optional, Tuple, Union

from fastapi import APIRouter

from ..http_response import KookitHTTPCallback, KookitHTTPResponse
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
        self.method_url_2_handler: Final[Dict[Tuple[str, str], KookitHTTPHandler]] = {}
        self.initial_callbacks: Final[List[KookitHTTPCallback]] = []
        self._service_url: str = service_url
        super().__init__(self.router)

    @property
    def service_url(self) -> str:
        return self._service_url

    @service_url.setter
    def service_url(self, new_service_url: str) -> None:
        self._service_url = new_service_url

    def add_actions(self, *actions: Union[KookitHTTPResponse, KookitHTTPCallback]) -> None:
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

        for handler in handlers:
            url, method = handler.url, handler.method
            try:
                self.method_url_2_handler[(method, url)].merge(handler)
            except KeyError:
                self.method_url_2_handler[(method, url)] = handler

        for (method, url), handler in self.method_url_2_handler.items():
            self.router.add_api_route(
                url,
                handler.__call__,
                methods=[method],
            )

    def clear_actions(self) -> None:
        self.method_url_2_handler.clear()

    def assert_completed(self):
        for handler in self.method_url_2_handler.values():
            handler.assert_completed()

    async def run(self) -> None:
        runner: KookitHTTPCallbackRunner = KookitHTTPCallbackRunner(self.initial_callbacks)
        await runner.run_callbacks()
