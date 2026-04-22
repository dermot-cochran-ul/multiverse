"""Tests for the Clock system."""
import pytest
from engine.consequence.clocks import Clock


def test_clock_creation():
    clock = Clock(name="Pressure", segments=4)
    assert clock.current == 0
    assert clock.segments == 4
    assert not clock.is_filled()


def test_clock_advance_with_justification():
    clock = Clock(name="Pressure", segments=4)
    filled = clock.advance(2, "Containment seal cracked under thermal stress.")
    assert clock.current == 2
    assert not filled


def test_clock_fills_on_completion():
    clock = Clock(name="Pressure", segments=3, current=2)
    filled = clock.advance(1, "Final seal failure observed.")
    assert filled
    assert clock.is_filled()
    assert clock.current == 3


def test_clock_does_not_exceed_segments():
    clock = Clock(name="Pressure", segments=3, current=2)
    clock.advance(5, "Catastrophic overpressure.")
    assert clock.current == 3


def test_clock_advance_without_justification_raises():
    clock = Clock(name="Pressure", segments=4)
    with pytest.raises(ValueError, match="justification"):
        clock.advance(1, "")


def test_clock_advance_with_blank_justification_raises():
    clock = Clock(name="Pressure", segments=4)
    with pytest.raises(ValueError, match="justification"):
        clock.advance(1, "   ")


def test_clock_advance_zero_amount_raises():
    clock = Clock(name="Pressure", segments=4)
    with pytest.raises(ValueError, match="amount"):
        clock.advance(0, "Some justification.")


def test_clock_segments_out_of_range_raises():
    with pytest.raises(ValueError):
        Clock(name="Bad", segments=0)
    with pytest.raises(ValueError):
        Clock(name="Bad", segments=7)


def test_clock_current_out_of_range_raises():
    with pytest.raises(ValueError):
        Clock(name="Bad", segments=3, current=4)
    with pytest.raises(ValueError):
        Clock(name="Bad", segments=3, current=-1)


def test_clock_trigger_effect_accessible():
    clock = Clock(name="Breach", segments=2, trigger_effect="containment_breach")
    clock.advance(2, "Breach confirmed.")
    assert clock.is_filled()
    assert clock.trigger_effect == "containment_breach"


def test_clock_serialization_roundtrip():
    clock = Clock(
        name="Test",
        segments=5,
        current=3,
        trigger_effect="test_effect",
        linked_clock_name="linked",
    )
    d = clock.to_dict()
    restored = Clock.from_dict(d)
    assert restored.name == clock.name
    assert restored.segments == clock.segments
    assert restored.current == clock.current
    assert restored.trigger_effect == clock.trigger_effect
    assert restored.linked_clock_name == clock.linked_clock_name
