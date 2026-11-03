# Five-Minute Interview Demo

## Problem

Teams adopting AI need to connect product decisions to official requirements and risk-management evidence. Generic LLMs can hallucinate obligations and provide no audit trail.

## Demo sequence

1. Open the Streamlit application and show the source register.
2. Ask: “What transparency duties may apply to a customer-service chatbot?”
3. Point out confidence, inline citations, source excerpts, and official links.
4. Open risk screening and assess the recruitment-ranking example.
5. Explain why the system is flagged as likely high-risk and show missing controls.
6. Open the evaluation tab and explain Recall@5, MRR, citation coverage, and offline reproducibility.

## Engineering decisions to explain

- BM25 catches exact legal terms; latent semantic retrieval handles paraphrases.
- A reranker boosts title, topic, and article matches.
- The evidence gate abstains instead of forcing an answer.
- Provider adapters separate retrieval quality from LLM choice.
- Audit events use trace IDs and avoid storing secrets.
- The offline generator makes CI deterministic and free of API dependency.

## Honest limitations

This is a student-built engineering prototype, not a legal product. A production version needs expert-labelled evaluation, access control, stronger document-ingestion security, scheduled source-refresh checks, and formal legal review.

