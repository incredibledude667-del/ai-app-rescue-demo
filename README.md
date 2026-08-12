# AI app rescue — verified before/after demo

This repository is a compact proof of a fixed-scope backend rescue. It starts with an AI-generated FastAPI service containing reproducible defects and ends with a tested repair.

## What the client would provide

- repository access;
- a reproducible bug list;
- expected endpoint responses or reference exports;
- a staging environment, if deployment is in scope.

## What is delivered

- corrected implementation;
- regression tests covering the acceptance contract;
- a before/after evidence script;
- a concise incident report and handoff commands.

## Verified rescue

The demo fixes six production-shaped failures: tenant data leakage, broken pagination, incorrect error semantics, unscoped search, case-sensitive search, and duplicate webhook processing.

| Acceptance check | Before | Rescued |
| --- | --- | --- |
| Tenant `acme` page 1 | Skips `inv_1` | Returns `inv_1`, `inv_3` |
| Reported tenant total | Incorrectly reports `3` | Correctly reports `2` |
| Cross-tenant invoice request | Leaks data with `200` | Hides it with `404` |
| Search for lowercase `north` | No result | Returns `inv_1` |
| Retried payment webhook | Processes twice | Detects duplicate; count stays `1` |

Current verification result: **6 acceptance tests passed**.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python -m scripts.compare_before_after
```

See [INCIDENT_REPORT.md](INCIDENT_REPORT.md) for the defect-to-test mapping.

The acceptance suite is CI-ready; the same two verification commands can be
added to any GitHub Actions, GitLab CI, or client pipeline.
