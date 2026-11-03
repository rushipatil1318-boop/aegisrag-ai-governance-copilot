from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from aegisrag import AegisRAG
from aegisrag.config import settings

st.set_page_config(page_title="AegisRAG", page_icon="🛡️", layout="wide")


@st.cache_resource
def load_rag() -> AegisRAG:
    return AegisRAG()


rag = load_rag()

st.title("🛡️ AegisRAG")
st.caption("Evidence-grounded EU AI governance copilot")
st.info(
    "This tool provides preliminary governance decision support. It is not legal advice or a "
    "conformity assessment."
)

with st.sidebar:
    st.subheader("Runtime")
    summary = rag.source_summary()
    st.metric("Official source notes", summary["documents"])
    st.metric("Searchable chunks", summary["chunks"])
    st.write(f"**Retrieval:** {summary['embedding_backend']}")
    st.write(f"**Generator:** {summary['llm_provider']}")
    st.write("Set `LLM_PROVIDER` in `.env` to use OpenAI-compatible, Ollama, or IBM watsonx.ai.")

ask_tab, assess_tab, evidence_tab, evaluation_tab = st.tabs(
    ["Ask with evidence", "Risk screening", "Source register", "Evaluation"]
)

with ask_tab:
    examples = [
        "What controls are expected for a high-risk AI system?",
        "What transparency duties may apply to a customer-service chatbot?",
        "How does the NIST AI RMF organize risk management activities?",
    ]
    selected = st.selectbox("Example question", [""] + examples)
    question = st.text_area("Question", value=selected, height=110)
    if st.button("Generate grounded answer", type="primary"):
        if len(question.strip()) < 3:
            st.warning("Enter a question.")
        else:
            with st.spinner("Planning, retrieving, verifying, and generating…"):
                answer = rag.ask(question)
            metric_a, metric_b, metric_c = st.columns(3)
            metric_a.metric("Confidence", f"{answer.confidence:.0%}")
            metric_b.metric("Evidence quality", answer.evidence_quality.title())
            metric_c.metric("Latency", f"{answer.latency_ms:.0f} ms")
            st.markdown(answer.answer)
            st.subheader("Evidence")
            for citation in answer.citations:
                with st.expander(
                    f"[{citation.citation_id}] {citation.reference} — {citation.title}"
                ):
                    st.write(citation.excerpt)
                    st.link_button("Open official source", citation.source_url)
            for warning in answer.warnings:
                st.warning(warning)

with assess_tab:
    st.subheader("Preliminary AI system risk screening")
    left, right = st.columns(2)
    with left:
        system_name = st.text_input("System name", "TalentMatch Candidate Ranking Assistant")
        purpose = st.text_area(
            "Intended purpose",
            "Rank job applicants and recommend a shortlist to human recruiters.",
            height=120,
        )
        employment = st.checkbox("Employment or recruitment", value=True)
        education = st.checkbox("Education or training")
        essential_services = st.checkbox("Essential services")
        medical = st.checkbox("Medical or health safety decisions")
        critical_infrastructure = st.checkbox("Critical infrastructure")
    with right:
        biometric = st.checkbox("Biometric processing")
        generative_ai = st.checkbox("Generates text, images, audio, or video", value=True)
        public_interaction = st.checkbox("Directly interacts with people")
        personal_data = st.checkbox("Processes personal data", value=True)
        human_oversight = st.checkbox("Human oversight control documented", value=True)
        risk_management = st.checkbox("Risk-management process documented")
        data_governance = st.checkbox("Data-governance controls documented")
        logging = st.checkbox("Automatic logging implemented")

    if st.button("Run risk screening"):
        assessment = rag.assess(
            {
                "system_name": system_name,
                "purpose": purpose,
                "impacts_individuals": True,
                "employment": employment,
                "education": education,
                "essential_services": essential_services,
                "medical": medical,
                "critical_infrastructure": critical_infrastructure,
                "biometric": biometric,
                "generative_ai": generative_ai,
                "public_interaction": public_interaction,
                "personal_data": personal_data,
                "human_oversight": human_oversight,
                "risk_management": risk_management,
                "data_governance": data_governance,
                "logging": logging,
            }
        )
        st.metric("Screening result", assessment.risk_level.title())
        st.progress(assessment.confidence, text=f"Confidence: {assessment.confidence:.0%}")
        st.markdown("#### Triggering factors")
        for item in assessment.triggers:
            st.write(f"- {item}")
        st.markdown("#### Likely obligations")
        for item in assessment.likely_obligations:
            st.write(f"- {item}")
        st.markdown("#### Control gaps")
        for item in assessment.control_gaps:
            st.write(f"- {item}")
        st.warning(assessment.disclaimer)

with evidence_tab:
    rows = [
        {
            "Source": document.source_id,
            "Framework": document.framework,
            "Reference": document.reference,
            "Title": document.title,
            "Verified": document.last_verified,
            "URL": document.source_url,
        }
        for document in rag.documents
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

with evaluation_tab:
    summary_path = Path(settings.artifact_dir) / "evaluation_summary.json"
    dashboard_path = Path(settings.artifact_dir) / "evaluation_dashboard.png"
    if summary_path.exists():
        evaluation = json.loads(summary_path.read_text(encoding="utf-8"))
        cols = st.columns(4)
        cols[0].metric("Recall@K", f"{evaluation['retrieval_recall_at_k']:.1%}")
        cols[1].metric("MRR", f"{evaluation['mean_reciprocal_rank']:.1%}")
        cols[2].metric("Citation coverage", f"{evaluation['citation_coverage']:.1%}")
        cols[3].metric("Avg latency", f"{evaluation['average_latency_ms']:.0f} ms")
        if dashboard_path.exists():
            st.image(str(dashboard_path), use_container_width=True)
    else:
        st.info("Run `python scripts/evaluate.py` to create the evaluation report.")

