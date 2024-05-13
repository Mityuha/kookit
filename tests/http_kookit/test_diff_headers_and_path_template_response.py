from typing import TYPE_CHECKING, Any

from kookit import Kookit, KookitXMLResponse


if TYPE_CHECKING:
    from httpx import Response


def test_diff_headers_and_path_template_response(
    faker: Any,
    kookit: Kookit,
) -> None:
    xml_response: str = "<xml>faker.pystr()</xml>"
    uri_path: str = "/catalog/{catalog_id}"
    service = kookit.new_http_service(
        actions=[
            KookitXMLResponse(
                xml_response,
                url=uri_path,
                method="POST",
                status_code=200,
            )
        ]
    )

    with kookit:
        response: Response = kookit.post(
            service,
            f"/catalog/{faker.pyint()}",
            json={"content-length": f"{faker.pyint()}"},
        )

    assert response.status_code == 200
    assert response.text == xml_response
