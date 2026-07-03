"""QA-04: 50 concurrent search requests against a running backend.

Usage:
    python backend/tests/load/search_load_test.py --base-url http://127.0.0.1:8000/api/v1
"""
from __future__ import annotations

import argparse
import asyncio
import statistics
import time
from dataclasses import dataclass

import httpx


QUERIES = [
    "тестовый",
    "документ",
    "инженерия",
    "практика",
    "алгоритм",
    "очередь",
    "лабораторная",
    "расписание",
    "зачет",
    "поиск",
]


@dataclass
class Sample:
    status_code: int
    elapsed_ms: float


async def login(client: httpx.AsyncClient) -> str:
    response = await client.post("/auth/demo", json={"role": "student"})
    response.raise_for_status()
    return response.json()["access_token"]


async def search_once(client: httpx.AsyncClient, token: str, query: str) -> Sample:
    started = time.perf_counter()
    response = await client.get(
        "/search",
        params={"q": query},
        headers={"Authorization": f"Bearer {token}"},
    )
    elapsed_ms = (time.perf_counter() - started) * 1000
    return Sample(status_code=response.status_code, elapsed_ms=elapsed_ms)


async def run_load(base_url: str, users: int) -> list[Sample]:
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        token = await login(client)
        tasks = [
            search_once(client, token, QUERIES[index % len(QUERIES)])
            for index in range(users)
        ]
        return await asyncio.gather(*tasks)


def percentile(values: list[float], ratio: float) -> float:
    if not values:
        return 0.0
    index = min(len(values) - 1, round((len(values) - 1) * ratio))
    return sorted(values)[index]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument("--users", type=int, default=50)
    args = parser.parse_args()

    samples = asyncio.run(run_load(args.base_url, args.users))
    durations = [sample.elapsed_ms for sample in samples]
    ok = sum(1 for sample in samples if sample.status_code == 200)

    print(f"requests={len(samples)} ok={ok} errors={len(samples) - ok}")
    print(f"avg_ms={statistics.mean(durations):.1f}")
    print(f"p50_ms={percentile(durations, 0.50):.1f}")
    print(f"p95_ms={percentile(durations, 0.95):.1f}")
    print(f"max_ms={max(durations):.1f}")


if __name__ == "__main__":
    main()
