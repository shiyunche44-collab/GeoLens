"""Fetches what the audit rules need. The only audit code allowed to touch the network."""

import ipaddress
import socket
from urllib.parse import urljoin, urlsplit

import httpx

from geolens.core.config import get_settings
from geolens.modules.audit.rules.base import SiteContext

BROWSER_UA = "Mozilla/5.0 (compatible; GeoLensAudit/0.1)"
_BOT_UA = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; {})"
PROBE_BOTS = {
    "GPTBot": _BOT_UA.format("GPTBot/1.2; +https://openai.com/gptbot"),
    "ClaudeBot": _BOT_UA.format("ClaudeBot/1.0; +claudebot@anthropic.com"),
    "PerplexityBot": _BOT_UA.format("PerplexityBot/1.0; +https://perplexity.ai/perplexitybot"),
}


class UnsafeTargetError(ValueError):
    pass


def assert_public_http_url(url: str) -> None:
    """SSRF guard: user-supplied URLs must be http(s) and resolve to public IPs."""
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise UnsafeTargetError("only absolute http(s) URLs are allowed")
    if get_settings().audit_allow_private_hosts:
        return
    for info in socket.getaddrinfo(parts.hostname, None):
        ip = ipaddress.ip_address(info[4][0])
        if not ip.is_global:
            raise UnsafeTargetError(f"{parts.hostname} resolves to non-public address {ip}")


def _get(
    client: httpx.Client, url: str, headers: dict[str, str] | None = None, max_hops: int = 3
) -> httpx.Response | None:
    """GET with manual redirects so every hop passes the SSRF guard.

    P2: pin the resolved IP in a custom transport to close the DNS-rebinding window.
    """
    for _ in range(max_hops + 1):
        assert_public_http_url(url)
        try:
            r = client.get(url, headers=headers)
        except httpx.HTTPError:
            return None
        if r.is_redirect and "location" in r.headers:
            url = urljoin(url, r.headers["location"])
            continue
        return r
    return None


def _text(r: httpx.Response | None) -> str | None:
    return r.text if r is not None and r.status_code < 400 else None


def fetch_site(url: str) -> SiteContext:
    assert_public_http_url(url)
    root = f"{urlsplit(url).scheme}://{urlsplit(url).netloc}/"
    timeout = get_settings().http_timeout_seconds
    with httpx.Client(
        timeout=timeout, headers={"User-Agent": BROWSER_UA}, follow_redirects=False
    ) as client:
        home = _get(client, url)
        robots = _get(client, urljoin(root, "/robots.txt"))
        llms = _get(client, urljoin(root, "/llms.txt"))
        probes: dict[str, int] = {}
        for bot, ua in PROBE_BOTS.items():
            r = _get(client, url, headers={"User-Agent": ua})
            if r is not None:
                probes[bot] = r.status_code
    return SiteContext(
        url=url,
        robots_txt=_text(robots),
        llms_txt=_text(llms),
        homepage_html=_text(home),
        homepage_status=home.status_code if home is not None else None,
        bot_probe_status=probes,
    )
