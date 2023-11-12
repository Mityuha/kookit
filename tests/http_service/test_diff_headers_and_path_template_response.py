from typing import Any

from httpx import Response

from kookit import Kookit, KookitHTTPService, KookitXMLResponse


async def test_diff_headers_and_path_template_response(
    faker: Any,
    kookit: Kookit,
) -> None:
    service = KookitHTTPService()

    xml_response: str = "<xml>faker.pystr()</xml>"
    uri_path: str = "/catalog/{catalog_id}"
    service = KookitHTTPService(
        actions=[
            KookitXMLResponse(
                xml_response,
                url=uri_path,
                method="POST",
                status_code=200,
            )
        ]
    )

    await kookit.prepare_services(service)
    await kookit.start_services()

    response: Response = await kookit.post(
        service,
        f"/catalog/{faker.pyint()}",
        json={"content-length": f"{faker.pyint()}"},
    )

    assert response.status_code == 200
    assert response.text == xml_response
