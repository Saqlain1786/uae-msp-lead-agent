from app.agent.reasoner import RuleBasedReasoner


def test_reasoner_scores_and_saves_strong_signal_candidate():
    reasoner = RuleBasedReasoner()
    evidence = {
        'text': 'managed it services and it support in dubai with outsourcing and hiring',
        'emails': ['sales@example.com'],
        'phones': ['+97141234567'],
        'uae_cities': ['Dubai'],
        'careers_page': 'https://example.com/careers',
        'contact_page': 'https://example.com/contact',
    }

    result = reasoner.evaluate(evidence)
    assert result.classification in {'MSP', 'IT Support Provider', 'Outsourcing Opportunity'}
    assert result.confidence_score >= 0.55
    assert result.save_decision is True
    assert len(result.detected_signals) >= 3


def test_reasoner_handles_insufficient_data():
    reasoner = RuleBasedReasoner()
    result = reasoner.evaluate({})
    assert result.save_decision is False
    assert result.explanation == 'insufficient data'
