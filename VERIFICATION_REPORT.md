# Verification Report

Verified on: 12 October 2026  
Runtime: Python 3.12.14  
Mode: Offline deterministic generation with LSA-TFIDF semantic retrieval

## Checks completed

| Check | Result |
|---|---|
| Automated test suite | 16 passed |
| Ruff code-quality check | Passed |
| Knowledge documents loaded | 16 |
| Searchable chunks generated | 29 |
| Evaluation questions executed | 10 |
| Retrieval Recall@5 | 1.00 |
| Mean Reciprocal Rank | 1.00 |
| Citation coverage | 1.00 |
| Answer keyword coverage | 0.675 |
| Executed notebook code cells | 6/6 |
| Notebook execution errors | 0 |
| FastAPI health endpoint | Healthy |
| Streamlit health endpoint | Healthy |

## Reproduction commands

```bash
python -m pytest -q
python -m ruff check aegisrag tests scripts app.py run_demo.py
python scripts/evaluate.py
python scripts/generate_demo.py
python scripts/build_notebook.py
```

## Important interpretation

The retrieval evaluation uses a compact labelled set included in the repository and is intended to demonstrate reproducible engineering, not to claim production or legal-grade performance. The offline answer generator is intentionally deterministic. External LLM performance must be evaluated separately before deployment.

