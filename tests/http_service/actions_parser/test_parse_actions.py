from typing import Any, List, Tuple

import pytest
from httpx import Request, Response

from kookit import groupby_actions, initial_requests


class Comparable:
    def __init__(self, number: int) -> None:
        self.number = number

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Comparable) and self.number == other.number

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.number})"


class Req(Comparable):
    def __init__(self, number: int) -> None:
        self.request = Request(method="GET", url="/")
        self.service = None
        super().__init__(number)


class Resp(Comparable):
    def __init__(self, number: int) -> None:
        self.response = Response(status_code=200)
        super().__init__(number)


@pytest.mark.parametrize(
    "actions, expected",
    (
        ([Req(1), Req(2), Req(3)], []),
        ([Resp(1), Resp(2), Resp(3)], [(Resp(1), []), (Resp(2), []), (Resp(3), [])]),
        ([Resp(1), Resp(2), Req(3)], [(Resp(1), []), (Resp(2), [Req(3)])]),
        ([Resp(1), Req(2), Resp(3)], [(Resp(1), [Req(2)]), (Resp(3), [])]),
        (
            [Req(1), Resp(2), Req(3), Req(4), Resp(5)],
            [(Resp(2), [Req(3), Req(4)]), (Resp(5), [])],
        ),
        (
            [Resp(1), Req(2), Req(3), Req(4)],
            [(Resp(1), [Req(2), Req(3), Req(4)])],
        ),
    ),
)
def test_group_by_actions(actions: List, expected: List[Tuple[Any, List]]) -> None:
    grouped_actions = groupby_actions(*actions)

    assert grouped_actions == expected


@pytest.mark.parametrize(
    "actions, expected",
    (
        ([Req(1), Req(2), Req(3)], [Req(1), Req(2), Req(3)]),
        ([Resp(1), Resp(2), Resp(3)], []),
        ([Resp(1), Resp(2), Req(3)], []),
        ([Req(1), Resp(2), Req(3), Req(4), Resp(5)], [Req(1)]),
        (
            [Req(1), Req(2), Req(3), Req(4)],
            [Req(1), Req(2), Req(3), Req(4)],
        ),
    ),
)
def test_initial_requests(actions: List, expected: List) -> None:
    initial_reqs = initial_requests(*actions)
    assert initial_reqs == expected
