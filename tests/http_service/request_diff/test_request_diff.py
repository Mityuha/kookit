from typing import Any

from kookit import compare_requests


async def test_bad_content(mocker: Any, faker: Any) -> None:
    req = mocker.Mock(content=faker.binary(10))
    freq = mocker.AsyncMock(**{"body.side_effect": [faker.binary(10)]})

    assert "body" in await compare_requests(freq, req)


async def test_bad_headers_subset(mocker: Any, faker: Any) -> None:
    req = mocker.Mock(content=b"", headers=faker.pydict(value_types=[str]))
    freq = mocker.AsyncMock(headers=faker.pydict(value_types=[str]))

    assert "headers" in await compare_requests(freq, req)


async def test_bad_query_string(mocker: Any, faker: Any) -> None:
    path: str = faker.uri_path()
    req = mocker.Mock(
        content=b"",
        headers={},
        url=mocker.Mock(
            path=path,
            query=faker.pystr(max_chars=10).encode("ascii"),
        ),
    )
    freq = mocker.AsyncMock(
        url=mocker.Mock(path=path, query=faker.pystr()),
        path_params=faker.pydict(value_types=[str]),
    )

    assert "query" in await compare_requests(freq, req)


async def test_request_with_path_params_ok(mocker: Any, faker: Any) -> None:
    path_params: dict = faker.pydict(3, value_types=[str])
    path = "/".join((faker.uri_path() + f"{{{k}}}") for k in path_params)
    query_string = faker.pystr()
    req = mocker.Mock(
        content=b"",
        headers={},
        url=mocker.Mock(
            path=path,
            query=query_string.encode("ascii"),
        ),
    )
    freq = mocker.AsyncMock(
        url=mocker.Mock(
            path=path.format(**path_params),
            query=query_string,
        ),
        path_params=path_params,
    )

    assert not await compare_requests(freq, req)
