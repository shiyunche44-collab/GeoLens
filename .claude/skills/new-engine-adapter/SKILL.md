---
name: new-engine-adapter
description: Add a generative AI engine (e.g. 文心一言, 腾讯元宝, Gemini, Google AI Overviews) to GeoLens collection. Use whenever the user asks to support/monitor/collect from a new AI engine or model provider.
---

# Add an engine adapter

Engines live in `apps/api/geolens/modules/collection/adapters/`. Read `base.py` (the
`EngineAdapter` contract) and `apps/api/geolens/modules/collection/README.md` first.

## 1. Pick the path

- **OpenAI-compatible `/chat/completions`** (DeepSeek, Kimi, 通义, 豆包, 混元, 智谱…):
  add ONE `EngineSpec(...)` line to `SPECS` in `openai_compatible.py`:
  `engine_id` (kebab/snake, stable forever), `display_name`, `region` (`cn` if it must be
  called from mainland China, else `global`), `base_url`, `default_model`, `key_env`,
  `fidelity` (`api_search` only if the API really performs web search, else `api_no_search`).
- **Anything else** (SERP API, Responses API with tools, browser automation): create
  `adapters/<engine>.py` with a class implementing `EngineAdapter` (`query` is async and
  returns the provider payload untouched in `RawResponse.payload`; `parse` turns it into
  `ParsedAnswer`). Register it in `adapters/__init__.py` with an `enabled=` credential check.
  `mode="browser"` adapters need an ADR (ToS / compliance) before merging.

## 2. Rules (enforced by CI)

- Network only through `httpx` inside `adapters/` (architecture test `test_external_deps`).
- Never parse-and-drop: the payload is persisted as the raw snapshot by the service.
- Report token/credit usage in `RawResponse.units` (and `cost_usd` when known) — it is metered.
- No secrets in code or fixtures; keys come from env (`.env.example` — add the key there).

## 3. Fixture + tests

1. Record a real (or faithfully shaped) response → `apps/api/tests/fixtures/engines/<engine_id>.json`
   with `{"prompt": ..., "response": <provider JSON>, "expect": {"min_citations": N}}`.
   Strip any IDs/keys. The contract test is parametrized over the registry and FAILS without it.
2. If the engine's citation format is new, add a case to `tests/golden/analysis_cases.json`
   (`from_raw_snapshot`) with the expected mentions/citations.
3. Run `make arch-check && make test`.

## 4. Finish

- Update the engine table in `docs/architecture.md` (§5) and `collection/README.md`.
- If it added a new region or mode, write an ADR (`/new-adr`).
