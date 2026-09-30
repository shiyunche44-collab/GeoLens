"""One adapter class, many engines: most CN and global LLM vendors expose an
OpenAI-compatible ``/chat/completions`` endpoint. Adding such an engine is a
new ``EngineSpec`` entry, not new code.

NOTE: plain chat completions usually run WITHOUT web search, so the answer can
differ from what users see in the product UI. ``fidelity`` records that.
"""

import os
import re
import time
from dataclasses import dataclass, field
from typing import Any

import httpx

from geolens.core.config import get_settings
from geolens.modules.collection.adapters.base import (
    CitationRef,
    Fidelity,
    Mode,
    ParsedAnswer,
    QueryRequest,
    RawResponse,
    Region,
    TransientEngineError,
)

_URL_RE = re.compile(r"https?://[^\s)\]>\"'，。]+")


@dataclass(frozen=True)
class EngineSpec:
    engine_id: str
    display_name: str
    region: Region
    base_url: str
    default_model: str
    key_env: str
    fidelity: Fidelity = "api_no_search"
    extra_body: dict[str, Any] = field(default_factory=dict[str, Any])

    @property
    def model_env(self) -> str:
        return f"GEOLENS_{self.engine_id.upper()}_MODEL"

    def api_key(self) -> str | None:
        return os.environ.get(self.key_env)

    def model(self) -> str:
        return os.environ.get(self.model_env, self.default_model)


# Model names change often — override with GEOLENS_<ENGINE>_MODEL.
SPECS: list[EngineSpec] = [
    EngineSpec(
        "deepseek",
        "DeepSeek",
        "cn",
        "https://api.deepseek.com/v1",
        "deepseek-chat",
        "DEEPSEEK_API_KEY",
    ),
    EngineSpec(
        "kimi",
        "Kimi (Moonshot)",
        "cn",
        "https://api.moonshot.cn/v1",
        "moonshot-v1-8k",
        "MOONSHOT_API_KEY",
    ),
    EngineSpec(
        "qwen",
        "通义千问",
        "cn",
        "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "qwen-plus",
        "DASHSCOPE_API_KEY",
    ),
    EngineSpec(
        "doubao",
        "豆包 (火山方舟)",
        "cn",
        "https://ark.cn-beijing.volces.com/api/v3",
        "doubao-seed-1-6",
        "ARK_API_KEY",
    ),
    EngineSpec(
        "chatgpt",
        "ChatGPT (API)",
        "global",
        "https://api.openai.com/v1",
        "gpt-4o-mini",
        "OPENAI_API_KEY",
    ),
    EngineSpec(
        "perplexity",
        "Perplexity Sonar",
        "global",
        "https://api.perplexity.ai",
        "sonar",
        "PERPLEXITY_API_KEY",
        fidelity="api_search",
    ),
]


class OpenAICompatibleAdapter:
    mode: Mode = "api"

    def __init__(self, spec: EngineSpec) -> None:
        self.spec = spec
        self.engine_id = spec.engine_id
        self.display_name = spec.display_name
        self.region: Region = spec.region
        self.fidelity: Fidelity = spec.fidelity

    async def query(self, req: QueryRequest) -> RawResponse:
        body = {
            "model": self.spec.model(),
            "messages": [{"role": "user", "content": req.prompt}],
            **self.spec.extra_body,
        }
        started = time.monotonic()
        async with httpx.AsyncClient(timeout=get_settings().http_timeout_seconds) as client:
            try:
                resp = await client.post(
                    f"{self.spec.base_url}/chat/completions",
                    json=body,
                    headers={"Authorization": f"Bearer {self.spec.api_key()}"},
                )
            except httpx.TransportError as e:
                raise TransientEngineError(f"{self.engine_id}: {e!r}") from e
        if resp.status_code == 429 or resp.status_code >= 500:
            raise TransientEngineError(f"{self.engine_id}: HTTP {resp.status_code}")
        resp.raise_for_status()
        payload: dict[str, Any] = resp.json()
        usage = payload.get("usage") or {}
        return RawResponse(
            engine_id=self.engine_id,
            payload=payload,
            model=payload.get("model"),
            latency_ms=int((time.monotonic() - started) * 1000),
            units=int(usage.get("total_tokens", 0)),
        )

    def parse(self, raw: RawResponse) -> ParsedAnswer:
        p = raw.payload
        text: str = p["choices"][0]["message"]["content"] or ""
        citations: list[CitationRef] = []
        if isinstance(p.get("search_results"), list):  # Perplexity (current)
            citations = [CitationRef(r["url"], r.get("title")) for r in p["search_results"]]
        elif isinstance(p.get("citations"), list):  # Perplexity (legacy)
            citations = [CitationRef(u) for u in p["citations"]]
        else:  # plain LLMs: harvest inline URLs
            seen: dict[str, None] = {}
            for m in _URL_RE.findall(text):
                seen.setdefault(m.rstrip(".,;"), None)
            citations = [CitationRef(u) for u in seen]
        return ParsedAnswer(text=text, citations=citations, model=raw.model)
