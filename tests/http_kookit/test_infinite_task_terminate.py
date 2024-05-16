import asyncio
from contextlib import asynccontextmanager, suppress
from typing import Any

import pytest

from kookit import Kookit, KookitJSONResponse
from kookit.logging import logger


async def infinite_task() -> None:
    while True:
        with suppress(asyncio.CancelledError):
            while True:
                logger.info("Please, stop me.")
                await asyncio.sleep(1.0)


@pytest.mark.parametrize("with_service", [False, True])
async def test_error_in_lifespan(
    kookit: Kookit,
    with_service: bool,
) -> None:
    service = kookit.new_http_service(unique_url=bool(with_service))

    @asynccontextmanager
    async def lifespan(_app: Any) -> Any:
        task = asyncio.create_task(infinite_task())
        yield
        task.cancel()
        await task

    service.add_lifespans(lifespan)
    service.add_actions(KookitJSONResponse({}, url="/url"))

    context: Any = service if with_service else kookit

    async with context(0.5, shutdown_timeout=0.5):
        assert (kookit.get(service, "/url")).json() == {}
