"""Test case: -> s1 -> s2 -> s3."""

from __future__ import annotations
import json
from dataclasses import dataclass
from typing import Any

import pytest

from kookit import IKookitHTTPService, Kookit, KookitJSONRequest, KookitJSONResponse


@dataclass
class IncomingRequest:
    method: str
    url: Any
    headers: Any
    json: dict


def create_service(
    kookit: Kookit,
    kookit_json_response_generator: Any,
    *,
    next_service: IKookitHTTPService,
    next_service_incoming: IncomingRequest,
    name: str,
) -> tuple[IncomingRequest, IKookitHTTPService]:
    kookit_json_response: KookitJSONResponse = kookit_json_response_generator()
    req = kookit_json_response.request
    incoming_request: IncomingRequest = IncomingRequest(
        method=req.method,
        url=req.url,
        headers=req.headers,
        json=json.loads(req.content),
    )
    request_to = KookitJSONRequest(
        next_service,
        method=next_service_incoming.method,
        url=next_service_incoming.url,
        headers=next_service_incoming.headers,
        json=next_service_incoming.json,
    )
    return incoming_request, kookit.new_http_service(
        actions=[
            kookit_json_response,
            request_to,
        ],
        name=name,
    )


# ruff: noqa: PT005


@pytest.fixture(name="service3")
def _service3(
    kookit: Kookit,
    kookit_json_response_generator: Any,
) -> tuple[IncomingRequest, IKookitHTTPService]:
    kookit_json_response: KookitJSONResponse = kookit_json_response_generator()
    req = kookit_json_response.request
    incoming_request: IncomingRequest = IncomingRequest(
        method=req.method,
        url=req.url,
        headers=req.headers,
        json=json.loads(req.content),
    )
    return incoming_request, kookit.new_http_service(
        actions=[kookit_json_response],
        name="service3",
    )


@pytest.fixture(name="service2")
def _service2(
    kookit: Kookit,
    service3: tuple[IncomingRequest, IKookitHTTPService],
    kookit_json_response_generator: Any,
) -> tuple[IncomingRequest, IKookitHTTPService]:
    return create_service(
        kookit,
        kookit_json_response_generator,
        next_service_incoming=service3[0],
        next_service=service3[1],
        name="service2",
    )


@pytest.fixture(name="service1")
def _service1(
    kookit: Any,
    service2: tuple[IncomingRequest, IKookitHTTPService],
    kookit_json_response_generator: Any,
) -> tuple[IncomingRequest, IKookitHTTPService]:
    return create_service(
        kookit,
        kookit_json_response_generator,
        next_service_incoming=service2[0],
        next_service=service2[1],
        name="service1",
    )


async def test_service_circle_requests(
    service1: tuple[IncomingRequest, IKookitHTTPService],
    kookit: Kookit,
) -> None:
    request, service_1 = service1

    async with kookit:
        kookit.request(
            service_1,
            method=request.method,
            url=request.url,
            headers=request.headers,
            json=request.json,
        )

        await kookit.asleep(1)
