from lead_funnel.stages import STAGES, parse_stage


def test_stage_order():
    assert STAGES == ("Lead", "Contacted", "Intro session", "Onboarded")


def test_parse_stage_normalizes_case_and_spaces():
    assert parse_stage(" intro  SESSION ") == 2
    assert parse_stage("lead") == 0
    assert parse_stage("Onboarded") == 3


def test_parse_stage_unknown():
    assert parse_stage("Won") is None
    assert parse_stage("") is None
    assert parse_stage(None) is None
