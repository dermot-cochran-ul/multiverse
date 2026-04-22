"""Tests for the deterministic resolution table."""
import pytest
from engine.consequence.resolution import (
    Effect,
    OutcomeDescriptor,
    Position,
    RESOLUTION_TABLE,
    resolve,
)


def test_all_combinations_present():
    """Every (Position, Effect) pair must be in the table."""
    for pos in Position:
        for eff in Effect:
            assert (pos, eff) in RESOLUTION_TABLE, (
                f"Missing combination: ({pos}, {eff})"
            )


@pytest.mark.parametrize(
    "position, effect, expected_segments, expected_multiplier",
    [
        (Position.CONTROLLED, Effect.LIMITED, 1, 0.5),
        (Position.CONTROLLED, Effect.STANDARD, 2, 1.0),
        (Position.CONTROLLED, Effect.GREAT, 3, 1.5),
        (Position.RISKY, Effect.LIMITED, 1, 1.0),
        (Position.RISKY, Effect.STANDARD, 2, 1.5),
        (Position.RISKY, Effect.GREAT, 3, 2.0),
        (Position.DESPERATE, Effect.LIMITED, 1, 1.5),
        (Position.DESPERATE, Effect.STANDARD, 2, 2.0),
        (Position.DESPERATE, Effect.GREAT, 3, 3.0),
    ],
)
def test_resolution_deterministic(
    position, effect, expected_segments, expected_multiplier
):
    outcome = resolve(position, effect)
    assert outcome.clock_segments_advanced == expected_segments
    assert outcome.cost_multiplier == expected_multiplier
    assert isinstance(outcome.description, str)
    assert len(outcome.description) > 0


def test_resolution_is_immutable():
    """Outcomes must be frozen (immutable)."""
    outcome = resolve(Position.RISKY, Effect.STANDARD)
    with pytest.raises((AttributeError, TypeError)):
        outcome.clock_segments_advanced = 99  # type: ignore[misc]


def test_resolution_returns_outcome_descriptor():
    result = resolve(Position.CONTROLLED, Effect.GREAT)
    assert isinstance(result, OutcomeDescriptor)


def test_higher_position_means_higher_cost():
    """More desperate position → higher cost multiplier (same effect)."""
    for eff in Effect:
        ctrl = resolve(Position.CONTROLLED, eff).cost_multiplier
        risky = resolve(Position.RISKY, eff).cost_multiplier
        desp = resolve(Position.DESPERATE, eff).cost_multiplier
        assert ctrl <= risky <= desp, f"Cost multiplier not monotone for effect {eff}"


def test_higher_effect_means_more_segments():
    """Greater effect → more clock segments advanced (same position)."""
    for pos in Position:
        lim = resolve(pos, Effect.LIMITED).clock_segments_advanced
        std = resolve(pos, Effect.STANDARD).clock_segments_advanced
        great = resolve(pos, Effect.GREAT).clock_segments_advanced
        assert lim <= std <= great, (
            f"Segment advancement not monotone for position {pos}"
        )
