"""Tests for cost application to player state."""
from engine.consequence.costs import CostDomain, apply_costs
from engine.world.state import Player


def make_player() -> Player:
    return Player(name="TestPlayer", location="Test Room")


def test_apply_single_cost():
    player = make_player()
    apply_costs(player, {CostDomain.PHYSICAL: 3})
    assert player.cost_pools["physical"] == 3


def test_apply_multiple_costs():
    player = make_player()
    apply_costs(
        player,
        {
            CostDomain.MATERIAL: 1,
            CostDomain.SOCIAL: 2,
            CostDomain.PSYCHOLOGICAL: 1,
        },
    )
    assert player.cost_pools["material"] == 1
    assert player.cost_pools["social"] == 2
    assert player.cost_pools["psychological"] == 1


def test_costs_accumulate():
    player = make_player()
    apply_costs(player, {CostDomain.PHYSICAL: 2})
    apply_costs(player, {CostDomain.PHYSICAL: 3})
    assert player.cost_pools["physical"] == 5


def test_all_domains_applicable():
    player = make_player()
    for domain in CostDomain:
        apply_costs(player, {domain: 1})
    for domain in CostDomain:
        assert player.cost_pools[domain.value] >= 1


def test_zero_cost_applies_cleanly():
    player = make_player()
    apply_costs(player, {CostDomain.MATERIAL: 0})
    assert player.cost_pools.get("material", 0) == 0


def test_costs_do_not_affect_other_fields():
    player = make_player()
    original_clarity = player.clarity_score
    original_location = player.location
    apply_costs(player, {CostDomain.SOCIAL: 5})
    assert player.clarity_score == original_clarity
    assert player.location == original_location
