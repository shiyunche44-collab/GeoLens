import pytest

from geolens.core.config import get_settings
from geolens.modules.audit.crawler import UnsafeTargetError, assert_public_http_url


@pytest.fixture
def strict_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "audit_allow_private_hosts", False)


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/",
        "http://127.0.0.1/",
        "http://10.0.0.5/admin",
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost:8000/",
        "http://[::1]/",
    ],
)
def test_ssrf_guard_rejects_non_public_targets(strict_guard: None, url: str) -> None:
    with pytest.raises(UnsafeTargetError):
        assert_public_http_url(url)


def test_ssrf_guard_accepts_public_ip(strict_guard: None) -> None:
    assert_public_http_url("http://93.184.215.14/")
