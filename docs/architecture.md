# Architecture

## Design goals

AegisRAG is designed for evidence traceability, deterministic evaluation, safe failure, provider portability, and local reproducibility. Retrieval, risk screening, generation, and reporting are separate components so each can be tested independently.

## Request lifecycle

1. The input guardrail normalises text, rejects common prompt-injection patterns, and redacts common personal identifiers.
2. The intent planner classifies the question and adds domain-specific retrieval terms.
3. The hybrid retriever combines custom BM25 scores with latent semantic vectors.
4. The reranker adds title, topic, article-number, and official-source relevance.
5. The evidence gate measures relevance and source diversity. Weak evidence causes abstention.
6. The selected generator receives only retrieved evidence and a strict grounded-answer prompt.
7. The citation validator removes unknown citation identifiers and guarantees a traceable evidence list.
8. An append-only JSONL audit event stores operational metadata without storing API secrets.

## Retrieval

BM25 is implemented directly in `aegisrag/retrieval.py`. The default semantic backend uses TF-IDF followed by Truncated SVD, producing lightweight latent-semantic vectors that run without model downloads. A Sentence Transformers backend can be enabled for dense embeddings.

Hybrid scores use lexical and semantic normalisation, followed by a lightweight metadata reranker. The retriever returns individual component scores for debugging and evaluation.

## Generation providers

- Offline evidence generator: deterministic, API-free and suitable for CI.
- OpenAI-compatible: works with compatible hosted model endpoints.
- Ollama: runs a local model.
- IBM watsonx.ai: obtains an IAM token and uses a watsonx project and Granite-compatible chat model.

Provider errors automatically fall back to the offline evidence generator and add a visible warning.

## Deployment surfaces

- `app.py`: Streamlit analyst interface.
- `aegisrag/api.py`: versioned REST endpoints and OpenAPI documentation.
- `Dockerfile`: API image.
- `docker-compose.yml`: API and UI services.
- `.github/workflows/ci.yml`: tests, linting, coverage, and evaluation.

