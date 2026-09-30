"""End-to-end demo against a running API using the mock engines.

make api worker   # or: GEOLENS_CELERY_EAGER=true make api   (no worker needed)
make demo
"""

import os
import sys
import time

import httpx

API = os.environ.get("GEOLENS_API_URL", "http://localhost:8000")


def main() -> None:
    c = httpx.Client(base_url=API, timeout=30)
    try:
        c.get("/healthz").raise_for_status()
    except httpx.HTTPError:
        sys.exit(f"API not reachable at {API} — start it with `make api`")

    pid = c.post("/projects", json={"name": f"Demo {time.strftime('%H:%M:%S')}"}).json()["id"]
    for brand in [
        {"name": "GeoLens", "domains": ["geolens.example.com"]},
        {"name": "RankPilot", "is_competitor": True, "domains": ["rankpilot.example.com"]},
        {"name": "Citely", "is_competitor": True, "domains": ["citely.example.com"]},
    ]:
        c.post(f"/projects/{pid}/brands", json=brand).raise_for_status()
    for q in [
        "最好的 GEO 分析工具有哪些？",
        "如何监测品牌在 AI 搜索里的曝光？",
        "Best tools to track brand visibility in ChatGPT?",
    ]:
        c.post(f"/projects/{pid}/prompts", json={"text": q}).raise_for_status()

    run = c.post(
        f"/projects/{pid}/runs",
        json={"engines": ["mock-cn", "mock-global"], "samples_per_prompt": 5},
    )
    run.raise_for_status()
    run_id = run.json()["id"]
    for _ in range(60):
        state = c.get(f"/runs/{run_id}").json()
        print(f"run {state['status']}: {state['done_tasks']}/{state['total_tasks']}")
        if state["status"] in ("completed", "failed"):
            break
        time.sleep(1)
    else:
        sys.exit("run did not finish — is a worker running? (`make worker`)")
    time.sleep(1)  # let analysis/metrics tasks drain

    metrics = c.get(f"/projects/{pid}/metrics").json()
    print(f"\n{'brand':<12}{'score':>8}{'mention':>10}{'SOV':>8}{'avg pos':>9}{'cited':>8}")
    for m in sorted(
        (m for m in metrics["summary"] if m["engine_id"] == "all"),
        key=lambda m: -m["visibility_score"],
    ):
        print(
            f"{m['brand_name']:<12}{m['visibility_score']:>8.1f}"
            f"{m['mention_rate']['value']:>10.0%}{m['share_of_voice'] or 0:>8.0%}"
            f"{m['avg_position'] or 0:>9.2f}{m['citation_rate']['value']:>8.0%}"
        )
    print(f"\nDashboard: http://localhost:3000/projects/{pid}/visibility")


if __name__ == "__main__":
    main()
