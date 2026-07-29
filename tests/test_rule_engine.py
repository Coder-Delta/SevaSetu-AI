from services.orchestrator.eligibility.rule_engine import (
    evaluate_eligibility,
    parse_age_range,
    parse_income_limit,
)


def test_parse_age_range_extracts_min_and_max() -> None:
    assert parse_age_range("Applicant must be between 18 and 35 years.") == (18, 35)


def test_parse_income_limit_handles_lakh_format() -> None:
    assert parse_income_limit("Family income should be less than 2.5 lakh per year.") == 250000.0


def test_evaluate_eligibility_scores_matching_profile() -> None:
    user_profile = {
        "age": 24,
        "income_bracket": "200000",
        "category": "SC",
        "location_state": "Karnataka",
    }
    scheme = {
        "id": "scheme-1",
        "scheme_name": "Ashadeepa Scheme",
        "eligibility": (
            "Applicant should be a resident of Karnataka. "
            "Applicant should belong to the Scheduled Caste (SC) category. "
            "Age should be between 18 and 35 years. "
            "Family income should be less than 2.5 lakh per year."
        ),
        "level": "State",
    }

    result = evaluate_eligibility(user_profile, scheme)

    assert result.is_potentially_eligible is True
    assert result.match_score > 0.7
    assert not result.unmatched_criteria
