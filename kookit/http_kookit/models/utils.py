from __future__ import annotations
from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from types import EllipsisType


T = TypeVar("T")


def none_if_ellipsis(value: T | EllipsisType) -> T | None:
    return value if value is not Ellipsis else None
