from typing import Any

from kookit import compare_requests


async def test_bad_content(mocker: Any, faker: Any) -> None:
    req = mocker.Mock(content=faker.binary(10))
    freq = mocker.AsyncMock(**{"body.side_effect": [faker.binary(10)]})

    assert await compare_requests(freq, req)
