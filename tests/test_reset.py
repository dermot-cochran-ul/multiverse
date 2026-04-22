"""Tests for player reset and memory retention."""
from engine.persistence.storage import reset_player
from engine.world.state import Player


def make_player() -> Player:
    p = Player(
        name="Rena",
        location="Archive",
        clarity_score=3.0,
        cost_pools={"social": 5, "physical": 2},
        memory={
            "anomaly_discovery": {"id": "a1"},
            "faction_debt": {"amount": 3},
            "trivial_note": "forgotten",
        },
        inventory=["key", "notebook"],
    )
    return p


def test_reset_clears_clarity():
    player = make_player()
    reset = reset_player(player, retain_memories=[])
    assert reset.clarity_score == 5.0


def test_reset_clears_cost_pools():
    player = make_player()
    reset = reset_player(player, retain_memories=[])
    assert reset.cost_pools == {}


def test_reset_clears_inventory():
    player = make_player()
    reset = reset_player(player, retain_memories=[])
    assert reset.inventory == []


def test_reset_retains_specified_memories():
    player = make_player()
    reset = reset_player(player, retain_memories=["anomaly_discovery"])
    assert "anomaly_discovery" in reset.memory
    assert reset.memory["anomaly_discovery"] == {"id": "a1"}


def test_reset_drops_unspecified_memories():
    player = make_player()
    reset = reset_player(player, retain_memories=["anomaly_discovery"])
    assert "faction_debt" not in reset.memory
    assert "trivial_note" not in reset.memory


def test_reset_retains_multiple_memories():
    player = make_player()
    reset = reset_player(
        player, retain_memories=["anomaly_discovery", "faction_debt"]
    )
    assert "anomaly_discovery" in reset.memory
    assert "faction_debt" in reset.memory
    assert "trivial_note" not in reset.memory


def test_reset_preserves_name_and_location():
    player = make_player()
    reset = reset_player(player, retain_memories=[])
    assert reset.name == "Rena"
    assert reset.location == "Archive"


def test_reset_with_nonexistent_memory_key_is_safe():
    """Requesting retention of a key that doesn't exist should not raise."""
    player = make_player()
    reset = reset_player(player, retain_memories=["does_not_exist"])
    assert "does_not_exist" not in reset.memory


def test_reset_returns_new_player_instance():
    player = make_player()
    reset = reset_player(player, retain_memories=[])
    assert reset is not player
