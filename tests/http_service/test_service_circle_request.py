"""Test case: -> s1 -> s2 -> s3."""

import json
from dataclasses import dataclass
from typing import Any, Tuple

import pytest

from kookit import Kookit, KookitHTTPService, KookitJSONRequest, KookitJSONResponse


@dataclass
class IncomingRequest:
    method: str
    url: Any
    headers: Any
    json: dict


def create_service(
    kookit_json_response_generator: Any,
    *,
    next_service: KookitHTTPService,
    next_service_incoming: IncomingRequest,
    name: str,
) -> Tuple[IncomingRequest, KookitHTTPService]:
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
    return incoming_request, KookitHTTPService(
        actions=[
            kookit_json_response,
            request_to,
        ],
        service_name=name,
    )


@pytest.fixture(name="service3")
def _service3(
    kookit_json_response_generator: Any,
) -> Tuple[IncomingRequest, KookitHTTPService]:
    kookit_json_response: KookitJSONResponse = kookit_json_response_generator()
    req = kookit_json_response.request
    incoming_request: IncomingRequest = IncomingRequest(
        method=req.method,
        url=req.url,
        headers=req.headers,
        json=json.loads(req.content),
    )
    return incoming_request, KookitHTTPService(
        actions=[kookit_json_response],
        service_name="service3",
    )


@pytest.fixture(name="service2")
def _service2(
    service3: Tuple[IncomingRequest, KookitHTTPService],
    kookit_json_response_generator: Any,
) -> Tuple[IncomingRequest, KookitHTTPService]:
    return create_service(
        kookit_json_response_generator,
        next_service_incoming=service3[0],
        next_service=service3[1],
        name="service2",
    )


@pytest.fixture(name="service1")
def _service1(
    service2: Tuple[IncomingRequest, KookitHTTPService],
    kookit_json_response_generator: Any,
) -> Tuple[IncomingRequest, KookitHTTPService]:
    return create_service(
        kookit_json_response_generator,
        next_service_incoming=service2[0],
        next_service=service2[1],
        name="service1",
    )


async def test_service_circle_requests(
    service1: Tuple[IncomingRequest, KookitHTTPService],
    service2: Any,
    service3: Any,
    kookit: Kookit,
) -> None:
    request, service_1 = service1

    await kookit.prepare_services(service_1, service2[1], service3[1])
    await kookit.start_services()

    await kookit.request(
        service_1,
        method=request.method,
        url=request.url,
        headers=request.headers,
        json=request.json,
    )

    await kookit.wait(1)
