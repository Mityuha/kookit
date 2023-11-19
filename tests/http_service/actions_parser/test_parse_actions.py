from typing import Any, List, Tuple

import pytest

from kookit import KookitHTTPRequest, KookitHTTPResponse, groupby_actions, initial_requests


class Comparable:
    def __init__(self, number: int) -> None:
        self.number = number

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Comparable) and self.number == other.number

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.number})"


class Req(Comparable, KookitHTTPRequest):
    def __init__(self, number: int) -> None:
        Comparable.__init__(self, number)
        KookitHTTPRequest.__init__(self, None, url="/", method="GET")  # type: ignore


class Resp(Comparable, KookitHTTPResponse):
    def __init__(self, number: int) -> None:
        Comparable.__init__(self, number)
        KookitHTTPResponse.__init__(self, url="/", method="POST")


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
