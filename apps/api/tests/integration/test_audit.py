import httpx
import pytest
import respx
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration

HOME = """<html><head><script type="application/ld+json">
{"@context":"https://schema.org","@type":"Organization","name":"Demo"}
</script></head><body>hi</body></html>"""


@respx.mock
def test_audit_reports_findings_and_score(client: TestClient) -> None:
    respx.get("https://demo.example.com/").mock(return_value=httpx.Response(200, text=HOME))
    respx.get("https://demo.example.com/robots.txt").mock(
        return_value=httpx.Response(200, text="User-agent: GPTBot\nDisallow: /\n")
    )
    respx.get("https://demo.example.com/llms.txt").mock(return_value=httpx.Response(404))

    r = client.post("/audits", json={"url": "https://demo.example.com/"})
    assert r.status_code == 202, r.text
    audit = client.get(f"/audits/{r.json()['id']}").json()

    assert audit["status"] == "done"
    rules = {f["rule_id"] for f in audit["findings"]}
    assert {"access.robots_ai_bots", "access.llms_txt", "trust.json_ld"} <= rules
    assert 0 <= audit["score"] < 100
