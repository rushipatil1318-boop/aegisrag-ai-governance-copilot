from __future__ import annotations

from dataclasses import dataclass
from typing import Any

HIGH_RISK_DOMAINS = {
    "employment": "employment, worker management, or access to self-employment",
    "education": "education or vocational training access and assessment",
    "essential_services": "access to essential private or public services",
    "law_enforcement": "law-enforcement decision support",
    "migration": "migration, asylum, or border-control decision support",
    "justice": "administration of justice or democratic processes",
    "critical_infrastructure": "safety management of critical infrastructure",
    "biometric": "biometric identification or categorisation",
    "medical": "medical-device or health-related safety decision support",
}

CONTROL_CHECKS = {
    "risk_management": "Document a continuous AI risk-management process.",
    "data_governance": "Establish data quality, provenance, representativeness, and bias controls.",
    "technical_documentation": "Prepare technical documentation and intended-purpose records.",
    "logging": "Enable traceable event logging and retain records under an approved policy.",
    "transparency_notice": "Provide clear instructions, limitations, and user-facing AI notices.",
    "human_oversight": "Define competent human oversight and intervention authority.",
    "accuracy_testing": "Define and test accuracy, robustness, and cybersecurity thresholds.",
    "post_market_monitoring": "Operate post-deployment monitoring and incident escalation.",
}


@dataclass(frozen=True)
class RiskDecision:
    risk_level: str
    confidence: float
    triggers: list[str]
    likely_obligations: list[str]
    control_gaps: list[str]
    recommended_actions: list[str]


def _truthy(data: dict[str, Any], key: str, default: bool = False) -> bool:
    value = data.get(key, default)
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "on"}
    return bool(value)


def assess_system(data: dict[str, Any]) -> RiskDecision:
    triggers: list[str] = []

    prohibited_checks = {
        "social_scoring": "Potential social-scoring use",
        "manipulative": "Potential manipulative or exploitative technique",
        "untargeted_face_scraping": "Potential untargeted facial-image scraping",
        "predictive_policing_only": "Individual criminal-risk prediction based only on profiling",
    }
    prohibited = [label for key, label in prohibited_checks.items() if _truthy(data, key)]
    if prohibited:
        triggers.extend(prohibited)
        risk_level = "potentially prohibited"
        confidence = 0.95
    else:
        high_risk = [
            description
            for key, description in HIGH_RISK_DOMAINS.items()
            if _truthy(data, key)
        ]
        if _truthy(data, "safety_component"):
            high_risk.append("AI used as a safety component of a regulated product or system")
        if high_risk and _truthy(data, "impacts_individuals", True):
            triggers.extend(high_risk)
            risk_level = "likely high-risk"
            confidence = min(0.93, 0.74 + 0.04 * len(high_risk))
        elif _truthy(data, "public_interaction") or _truthy(data, "generative_ai"):
            triggers.append("Direct interaction with people or generation of synthetic content")
            risk_level = "transparency obligations likely"
            confidence = 0.82
        else:
            triggers.append("No high-risk or transparency trigger selected in this screening")
            risk_level = "minimal or limited risk"
            confidence = 0.68

    if risk_level == "potentially prohibited":
        obligations = [
            "Pause deployment and obtain qualified legal and governance review.",
            "Document the intended purpose, affected groups, and applicable exceptions.",
        ]
    elif risk_level == "likely high-risk":
        obligations = [
            "Risk management throughout the AI system lifecycle",
            "Data and data-governance controls",
            "Technical documentation and automatic logging",
            "Transparency and instructions for deployers",
            "Effective human oversight",
            "Accuracy, robustness, and cybersecurity controls",
            "Post-market monitoring and incident management",
        ]
    elif risk_level == "transparency obligations likely":
        obligations = [
            "Inform people when they interact with an AI system where applicable",
            "Mark or disclose AI-generated or manipulated content where applicable",
            "Maintain accessible usage limitations and escalation routes",
        ]
    else:
        obligations = [
            "Apply voluntary responsible-AI controls and document the screening decision",
            "Monitor for material changes that could alter the risk classification",
        ]

    control_gaps = [message for key, message in CONTROL_CHECKS.items() if not _truthy(data, key)]
    recommended_actions = [
        "Validate the classification against the complete current legal text and Annex III.",
        "Assign accountable owners for governance, security, privacy, and human oversight.",
        "Create measurable acceptance criteria and retain evidence from testing.",
    ]
    if _truthy(data, "personal_data"):
        recommended_actions.append(
            "Coordinate the AI assessment with privacy and data-protection review."
        )
    if risk_level == "likely high-risk" and _truthy(data, "public_body"):
        recommended_actions.append(
            "Evaluate whether a fundamental-rights impact assessment is required."
        )

    return RiskDecision(
        risk_level=risk_level,
        confidence=round(confidence, 3),
        triggers=triggers,
        likely_obligations=obligations,
        control_gaps=control_gaps,
        recommended_actions=recommended_actions,
    )

