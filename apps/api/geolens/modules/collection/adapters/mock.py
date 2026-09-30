"""Deterministic fake engine for tests, local demos and CI. No network."""

import hashlib
import random

from geolens.modules.collection.adapters.base import (
    CitationRef,
    Fidelity,
    Mode,
    ParsedAnswer,
    QueryRequest,
    RawResponse,
    Region,
)

CANDIDATES = ["GeoLens", "RankPilot", "Citely", "AnswerScope", "SerpNova"]


class MockAdapter:
    mode: Mode = "mock"
    fidelity: Fidelity = "synthetic"

    def __init__(self, engine_id: str, region: Region) -> None:
        self.engine_id = engine_id
        self.display_name = f"Mock ({region})"
        self.region: Region = region

    async def query(self, req: QueryRequest) -> RawResponse:
        seed = hashlib.sha256(f"{self.engine_id}|{req.prompt}|{req.sample_idx}".encode()).digest()
        rng = random.Random(seed)
        picked = rng.sample(CANDIDATES, k=rng.randint(2, 4))
        lines = [f"{i}. **{name}**：适合做 AI 搜索可见度分析。" for i, name in enumerate(picked, 1)]
        sources = [f"https://{name.lower()}.example.com/features" for name in picked[:2]]
        text = "以下是一些常见选择：\n" + "\n".join(lines)
        payload = {"answer": text, "sources": [{"url": u, "title": None} for u in sources]}
        return RawResponse(engine_id=self.engine_id, payload=payload, model="mock-1", units=1)

    def parse(self, raw: RawResponse) -> ParsedAnswer:
        sources = raw.payload.get("sources", [])
        return ParsedAnswer(
            text=raw.payload["answer"],
            citations=[CitationRef(url=s["url"], title=s.get("title")) for s in sources],
            model=raw.model,
        )
