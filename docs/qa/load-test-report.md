# QA-04 Load Test Report

## Scope

Scenario: 50 concurrent `GET /api/v1/search?q=...` requests from authenticated demo student.

Script:

```bash
python backend/tests/load/search_load_test.py --base-url http://127.0.0.1:8000/api/v1 --users 50
```

## Environment

- Backend: FastAPI app from this repository
- Dependencies: PostgreSQL, Elasticsearch, Redis from `docker-compose.yml`
- Auth: `POST /api/v1/auth/demo` with `student`
- Dataset: documents uploaded through QA-03 flow before running the load test

## Acceptance Metrics

| Metric | Target |
| --- | ---: |
| Concurrent requests | 50 |
| Successful responses | 50/50 |
| Error responses | 0 |
| Reported values | average, p50, p95, max latency |

## Baseline Result Template

Fill this table after running the command on the assembled stack.

| Run date | Dataset | OK | Errors | Avg ms | P50 ms | P95 ms | Max ms |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2026-07-03 | QA fixture corpus | pending | pending | pending | pending | pending | pending |

## Notes

The script intentionally logs compact numeric output so it can be pasted into this report or CI artifacts without extra processing.
