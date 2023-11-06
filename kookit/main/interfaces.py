from typing import Any, Optional, Protocol

from fastapi import APIRouter


class IKookitService(Protocol):
    service_url: str

    @property
    def url_env_var(self) -> Optional[str]:
        ...

    @property
    def router(self) -> APIRouter:
        ...

    async def run(self) -> None:
        ...

    def unused_responses(self) -> list[Any]:
        ...
