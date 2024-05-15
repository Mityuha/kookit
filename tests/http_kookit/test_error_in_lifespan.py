from contextlib import asynccontextmanager
from typing import Any

import pytest

from kookit import Kookit, KookitJSONResponse


@pytest.mark.parametrize("with_service", [False, True])
def test_error_in_lifespan(
    kookit: Kookit,
    with_service: bool,
) -> None:
    service = kookit.new_http_service(unique_url=bool(with_service))

    @asynccontextmanager
    async def lifespan(_app: Any) -> Any:
        msg = "some error"
        raise ValueError(msg)
        yield

    service.add_lifespans(lifespan)
    service.add_actions(KookitJSONResponse({}, url="/url"))

    context: Any = service if with_service else kookit

    with pytest.raises(RuntimeError), context(0.5):
        kookit.sleep(1.0)
