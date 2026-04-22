"""Tests for entity archetypes."""
from engine.entities.nai import Nai
from engine.entities.court_fae import CourtFae
from engine.entities.gilded_saint import GildedSaint
from engine.world.state import WorldState, Player, Location


def make_world(player_clarity: float = 7.0) -> WorldState:
    world = WorldState(world_id="test_world")
    world.locations["Hall"] = Location(
        name="Hall",
        description_tags=["stone_floor", "torchlit"],
    )
    world.players["Hero"] = Player(
        name="Hero",
        location="Hall",
        clarity_score=player_clarity,
    )
    return world


# ---------------------------------------------------------------------------
# Nai
# ---------------------------------------------------------------------------


def test_nai_deposits_clarity_residue():
    world = make_world()
    nai = Nai(name="Whisper", location="Hall")
    events = nai.act(world)
    assert any(e.event_type == "residue_deposited" for e in events)
    assert len(nai.traces) == 1
    residue = nai.traces[0]
    assert "clarity_residue" in residue.description_tags


def test_nai_increases_player_clarity():
    world = make_world(player_clarity=6.0)
    nai = Nai(name="Whisper", location="Hall")
    nai.act(world)
    assert world.players["Hero"].clarity_score == 7.0


def test_nai_evidence_stored_in_world():
    world = make_world()
    nai = Nai(name="Whisper", location="Hall")
    nai.act(world)
    assert any("clarity_residue" in k for k in world.evidence_store)


def test_nai_evidence_added_to_location():
    world = make_world()
    nai = Nai(name="Whisper", location="Hall")
    nai.act(world)
    loc = world.locations["Hall"]
    assert any("clarity_residue" in eid for eid in loc.evidence_present)


def test_nai_no_action_in_unknown_location():
    world = make_world()
    nai = Nai(name="Whisper", location="Nowhere")
    events = nai.act(world)
    assert events == []


# ---------------------------------------------------------------------------
# CourtFae
# ---------------------------------------------------------------------------


def test_court_fae_deposits_glamour_and_debt():
    world = make_world()
    fae = CourtFae(name="Sable", location="Hall")
    fae.act(world)
    assert len(fae.traces) == 2
    trace_types = [t.description_tags[0] for t in fae.traces]
    assert "glamour_residue" in trace_types
    assert "debt_marker" in trace_types


def test_court_fae_high_clarity_minor_social_cost():
    world = make_world(player_clarity=8.0)
    fae = CourtFae(name="Sable", location="Hall")
    fae.act(world)
    player = world.players["Hero"]
    # At high clarity only social cost of 1 is imposed
    assert player.cost_pools.get("social", 0) == 1
    assert player.cost_pools.get("psychological", 0) == 0


def test_court_fae_low_clarity_amplified_costs():
    world = make_world(player_clarity=3.0)
    fae = CourtFae(name="Sable", location="Hall")
    fae.act(world)
    player = world.players["Hero"]
    assert player.cost_pools.get("social", 0) == 2
    assert player.cost_pools.get("psychological", 0) == 1


def test_court_fae_events_returned():
    world = make_world()
    fae = CourtFae(name="Sable", location="Hall")
    events = fae.act(world)
    assert len(events) >= 2


# ---------------------------------------------------------------------------
# GildedSaint
# ---------------------------------------------------------------------------


def test_gilded_saint_deposits_penance_and_ledger():
    world = make_world()
    saint = GildedSaint(name="Aurelius", location="Hall")
    saint.act(world)
    assert len(saint.traces) == 2
    trace_types = [t.description_tags[0] for t in saint.traces]
    assert "penance_residue" in trace_types
    assert "virtue_ledger_entry" in trace_types


def test_gilded_saint_normal_clarity_costs():
    world = make_world(player_clarity=6.0)
    saint = GildedSaint(name="Aurelius", location="Hall")
    saint.act(world)
    player = world.players["Hero"]
    assert player.cost_pools.get("psychological", 0) == 1
    assert player.cost_pools.get("social", 0) == 1


def test_gilded_saint_low_clarity_doubled_costs():
    world = make_world(player_clarity=3.0)
    saint = GildedSaint(name="Aurelius", location="Hall")
    saint.act(world)
    player = world.players["Hero"]
    assert player.cost_pools.get("psychological", 0) == 2
    assert player.cost_pools.get("social", 0) == 2


def test_gilded_saint_events_returned():
    world = make_world()
    saint = GildedSaint(name="Aurelius", location="Hall")
    events = saint.act(world)
    assert len(events) >= 2
