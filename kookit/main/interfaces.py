from typing import Any, Iterable, Protocol

from pytest_mock import MockerFixture


UnfitService = Any


class IKookit(Protocol):
    def __init__(self, mocker: MockerFixture) -> None:
        ...

    async def prepare_services(self, *services: Any) -> Iterable[UnfitService]:
        ...

    async def start_services(self, **_kwargs: Any) -> None:
        ...

    async def stop_services(self, **_kwargs: Any) -> None:
        ...
