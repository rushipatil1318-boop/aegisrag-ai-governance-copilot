# Portfolio and CV Entry

## Project title

**AegisRAG — Evidence-Grounded AI Governance Copilot**

## One-line portfolio description

Built an enterprise-style Generative AI governance copilot that combines hybrid RAG, EU AI Act and NIST AI RMF evidence, risk screening, verified citations, guardrails, FastAPI, Streamlit, Docker, and reproducible evaluation.

## CV bullets

- Developed an evidence-grounded Generative AI copilot using custom BM25 plus latent-semantic hybrid retrieval, reranking, confidence-based abstention, and citation validation across official EU AI Act and NIST AI RMF sources.
- Implemented an AI-system risk-screening and control-gap workflow with prompt-injection detection, PII redaction, traceable audit events, and provider adapters for IBM watsonx.ai, OpenAI-compatible endpoints, Ollama, and deterministic offline execution.
- Delivered a deployment-ready FastAPI and Streamlit application with Docker, GitHub Actions, 16 automated tests, an executed notebook, and a reproducible evaluation achieving 100% Recall@5 and 100% citation coverage on the included benchmark.

## Interview explanation

The most important engineering choice was separating retrieval and evidence quality from LLM fluency. The application can be tested without an API key, while hosted or local LLMs can be selected through configuration. This makes evaluation reproducible and avoids hiding retrieval failures behind a fluent model response.

