from typing import Any, List, Optional, Protocol, runtime_checkable

from fastapi import APIRouter
from typing_extensions import TypeGuard


@runtime_checkable
class IKookitHTTPService(Protocol):
    service_url: str

    @property
    def url_env_var(self) -> Optional[str]:
        ...

    @property
    def router(self) -> APIRouter:
        ...

    async def run(self) -> None:
        ...

    def unused_responses(self) -> List[Any]:
        ...


def http_service(service: Any) -> TypeGuard[IKookitHTTPService]:
    return isinstance(service, IKookitHTTPService)
