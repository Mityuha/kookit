from itertools import groupby
from typing import Any, List, Tuple, Union

from typing_extensions import TypeGuard

from .interfaces import IKookitHTTPRequest, IKookitHTTPResponse


def is_response(
    action: Union[IKookitHTTPResponse, IKookitHTTPRequest]
) -> TypeGuard[IKookitHTTPResponse]:
    return hasattr(action, "request") and isinstance(action, IKookitHTTPResponse)


def is_request(
    action: Union[IKookitHTTPResponse, IKookitHTTPRequest]
) -> TypeGuard[IKookitHTTPRequest]:
    return isinstance(action, IKookitHTTPRequest) and hasattr(action, "service")


def initial_requests(
    *actions: Union[IKookitHTTPResponse, IKookitHTTPRequest]
) -> List[IKookitHTTPRequest]:
    initial_requests: List[IKookitHTTPRequest] = []
    for action in actions:
        if is_request(action):
            initial_requests.append(action)
        else:
            break
    return initial_requests


def groupby_actions(
    *actions: Union[IKookitHTTPResponse, IKookitHTTPRequest],
) -> List[Tuple[IKookitHTTPResponse, List[IKookitHTTPRequest]]]:
    response_i: int = 0
    for response_i, action in enumerate(actions):
        if not is_request(action):
            break
    else:
        response_i += 1

    def action_key(action: Any) -> int:
        assert is_response(action) or is_request(action)
        return is_response(action)

    gactions: List = []
    for is_resp, group in groupby(actions[response_i:], action_key):
        if is_resp:
            for response in group:
                gactions.append((response, []))
        else:
            gactions[-1][1].extend(list(group))

    return gactions
