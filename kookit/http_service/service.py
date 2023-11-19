from itertools import chain
from typing import Dict, Final, Iterable, List, Tuple, Union

from fastapi import APIRouter
from httpx import URL

from ..logging import logger
from .actions_parser import groupby_actions, initial_requests
from .http_handler import KookitHTTPHandler
from .interfaces import IKookitHTTPRequest, IKookitHTTPResponse
from .request_runner import KookitHTTPRequestRunner


class KookitHTTPService:
    def __init__(
        self,
        url_env_var: str = "",
        *,
        service_url: str = "",
        actions: Iterable[Union[IKookitHTTPRequest, IKookitHTTPResponse]] = (),
        routers: Iterable[APIRouter] = (),
        service_name: str = "",
    ) -> None:
        self.url_env_var: str = url_env_var
        self.service_url: str = service_url
        self.router: Final[APIRouter] = APIRouter()
        self.method_url_2_handler: Final[Dict[Tuple[str, URL], KookitHTTPHandler]] = {}
        self.initial_requests: Final[List[IKookitHTTPRequest]] = []
        self.service_name: Final[str] = service_name or self.__class__.__name__

        self.add_routers(*routers)
        self.add_actions(*actions)

    def __str__(self) -> str:
        return f"[{self.service_name}]"

    def __repr__(self) -> str:
        return str(self)

    def add_routers(self, *routers: APIRouter) -> None:
        for router in routers:
            self.router.include_router(router)

    def add_actions(self, *actions: Union[IKookitHTTPResponse, IKookitHTTPRequest]) -> None:
        self.initial_requests.extend(initial_requests(*actions))
        grouped_actions: List[
            Tuple[IKookitHTTPResponse, List[IKookitHTTPRequest]]
        ] = groupby_actions(*actions)

        handlers: Iterable[KookitHTTPHandler] = (
            KookitHTTPHandler(
                resp,
                service_name=self.service_name,
                requests=requests,
            )
            for (resp, requests) in grouped_actions
        )

        for handler in handlers:
            url, method = handler.url, handler.method
            try:
                self.method_url_2_handler[(method, url)].merge(handler)
            except KeyError:
                self.method_url_2_handler[(method, url)] = handler

        for (method, url), handler in self.method_url_2_handler.items():
            self.router.add_api_route(
                url.path,
                handler.__call__,
                methods=[method],
            )
        logger.trace(
            f"{self}: handlers {self.method_url_2_handler}, {len(self.initial_requests)} initial requests {self.initial_requests}"
        )

    def unused_responses(self) -> List[IKookitHTTPResponse]:
        unused_responses: List[IKookitHTTPResponse] = list(
            chain.from_iterable(
                handler.unused_responses() for handler in self.method_url_2_handler.values()
            )
        )

        logger.trace(f"{self}: {len(unused_responses)} unused responses: {unused_responses}")
        return unused_responses

    async def run(self) -> None:
        runner: KookitHTTPRequestRunner = KookitHTTPRequestRunner(
            self.initial_requests,
            service_name=self.service_name,
        )
        await runner.run_requests()
