from aegisrag.risk import assess_system


def test_recruitment_system_is_likely_high_risk():
    result = assess_system(
        {
            "purpose": "Rank job applicants",
            "employment": True,
            "impacts_individuals": True,
        }
    )
    assert result.risk_level == "likely high-risk"
    assert any("employment" in trigger for trigger in result.triggers)


def test_chatbot_gets_transparency_screening():
    result = assess_system(
        {
            "purpose": "Answer customer questions",
            "public_interaction": True,
            "generative_ai": True,
        }
    )
    assert result.risk_level == "transparency obligations likely"


def test_prohibited_trigger_stops_normal_classification():
    result = assess_system({"purpose": "Score citizens", "social_scoring": True})
    assert result.risk_level == "potentially prohibited"
    assert result.confidence >= 0.9

