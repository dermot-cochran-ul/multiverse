"""Tests for the Clarity system."""
from engine.clarity.clarity import ClarityState
from engine.consequence.costs import CostDomain


def test_default_clarity_score():
    state = ClarityState()
    assert state.score == 5.0


def test_clarity_increase():
    state = ClarityState(score=5.0)
    state.increase(2.0)
    assert state.score == 7.0


def test_clarity_decrease():
    state = ClarityState(score=5.0)
    state.decrease(3.0)
    assert state.score == 2.0


def test_clarity_clamped_at_max():
    state = ClarityState(score=9.0)
    state.increase(5.0)
    assert state.score == 10.0


def test_clarity_clamped_at_min():
    state = ClarityState(score=1.0)
    state.decrease(5.0)
    assert state.score == 0.0


def test_high_clarity_reduces_social_vulnerability():
    state = ClarityState(score=9.0)
    mods = state.vulnerability_modifiers()
    assert mods[CostDomain.SOCIAL] < 1.0
    assert mods[CostDomain.PSYCHOLOGICAL] < 1.0


def test_mid_clarity_neutral_vulnerability():
    state = ClarityState(score=6.0)
    mods = state.vulnerability_modifiers()
    assert mods[CostDomain.SOCIAL] == 1.0
    assert mods[CostDomain.PSYCHOLOGICAL] == 1.0


def test_low_clarity_increases_social_vulnerability():
    state = ClarityState(score=2.0)
    mods = state.vulnerability_modifiers()
    assert mods[CostDomain.SOCIAL] > 1.0
    assert mods[CostDomain.PSYCHOLOGICAL] > 1.0


def test_very_low_clarity_maximum_vulnerability():
    state = ClarityState(score=1.0)
    mods = state.vulnerability_modifiers()
    assert mods[CostDomain.SOCIAL] == 2.0
    assert mods[CostDomain.PSYCHOLOGICAL] == 2.5


def test_material_physical_informational_unaffected_by_clarity():
    """These domains must not be amplified by clarity changes."""
    for score in [0.0, 5.0, 10.0]:
        state = ClarityState(score=score)
        mods = state.vulnerability_modifiers()
        assert mods[CostDomain.MATERIAL] == 1.0
        assert mods[CostDomain.PHYSICAL] == 1.0
        assert mods[CostDomain.INFORMATIONAL] == 1.0


def test_vulnerability_modifiers_returns_all_domains():
    state = ClarityState()
    mods = state.vulnerability_modifiers()
    for domain in CostDomain:
        assert domain in mods
