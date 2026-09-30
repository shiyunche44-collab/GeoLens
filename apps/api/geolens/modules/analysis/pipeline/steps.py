import re
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from geolens.modules.analysis.pipeline.base import BrandRef, CitationFact, MentionFact

_TRACKING_PARAMS = re.compile(r"^(utm_|spm$|from$|ref$)")
_SNIPPET_RADIUS = 40


def normalize_text(text: str) -> str:
    """NFKC folds full-width ASCII (ＧｅｏＬｅｎｓ → GeoLens); casefold for matching."""
    return unicodedata.normalize("NFKC", text).casefold()


def _is_ascii_word(term: str) -> bool:
    return all(ord(c) < 128 for c in term)


def _find(term: str, haystack: str) -> int:
    """Earliest index of term; ASCII terms must sit on word boundaries."""
    needle = normalize_text(term).strip()
    if not needle:
        return -1
    if _is_ascii_word(needle):
        m = re.search(rf"(?<![0-9a-z]){re.escape(needle)}(?![0-9a-z])", haystack)
        return m.start() if m else -1
    return haystack.find(needle)


def match_brands(text: str, brands: list[BrandRef]) -> list[MentionFact]:
    haystack = normalize_text(text)
    hits: list[tuple[int, BrandRef]] = []
    for brand in brands:
        idxs = [i for i in (_find(t, haystack) for t in [brand.name, *brand.aliases]) if i >= 0]
        if idxs:
            hits.append((min(idxs), brand))
    hits.sort(key=lambda h: h[0])
    plain = unicodedata.normalize("NFKC", text)
    return [
        MentionFact(
            brand_id=brand.id,
            position=rank,
            snippet=plain[max(0, idx - _SNIPPET_RADIUS) : idx + _SNIPPET_RADIUS].strip(),
        )
        for rank, (idx, brand) in enumerate(hits, 1)
    ]


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = (parts.hostname or "").lower().removeprefix("www.")
    query = urlencode([(k, v) for k, v in parse_qsl(parts.query) if not _TRACKING_PARAMS.match(k)])
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower() or "https", host, path, query, ""))


def domain_of(url: str) -> str:
    # P2: use the Public Suffix List (tldextract) for registrable domains.
    return (urlsplit(url).hostname or "").lower().removeprefix("www.")


def _owner(domain: str, brands: list[BrandRef]) -> BrandRef | None:
    for brand in brands:
        for d in brand.domains:
            d = d.lower().removeprefix("www.")
            if domain == d or domain.endswith("." + d):
                return brand
    return None


def extract_citations(urls: list[str], brands: list[BrandRef]) -> list[CitationFact]:
    seen: dict[str, None] = {}
    for u in urls:
        if u.startswith(("http://", "https://")):
            seen.setdefault(normalize_url(u), None)
    facts: list[CitationFact] = []
    for pos, url in enumerate(seen, 1):
        domain = domain_of(url)
        owner = _owner(domain, brands)
        facts.append(
            CitationFact(url=url, domain=domain, position=pos, brand_id=owner.id if owner else None)
        )
    return facts
