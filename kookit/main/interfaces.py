from typing import Optional, Protocol

from fastapi import APIRouter


class IKookitService(Protocol):
    @property
    def url_env_var(self) -> Optional[str]:
        ...

    @property
    def router(self) -> APIRouter:
        ...

    async def run(self) -> None:
        ...
