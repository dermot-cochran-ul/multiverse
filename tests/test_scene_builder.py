"""Tests for the scene builder."""
import pytest
from engine.narrative.scene_builder import build_scene, SceneOutput, Choice
from engine.world.state import WorldState, Player, Location
from engine.consequence.clocks import Clock
from engine.investigation.anomalies import Anomaly
from engine.investigation.hypotheses import Hypothesis
from engine.investigation.evidence import Evidence


def make_world() -> WorldState:
    world = WorldState(world_id="scene_test")
    world.locations["Workshop"] = Location(
        name="Workshop",
        description_tags=["cluttered", "dim_lighting"],
        connections=["Courtyard"],
        evidence_present=["ev1"],
    )
    world.players["Lyra"] = Player(
        name="Lyra",
        location="Workshop",
        clarity_score=6.0,
        cost_pools={"physical": 2},
    )
    world.evidence_store["ev1"] = Evidence(
        id="ev1",
        type="residue",
        description_tags=["soot_trace"],
    ).to_dict()

    world.clocks["clock1"] = Clock(
        name="Fire Risk",
        segments=4,
        current=2,
        trigger_effect="fire_breaks_out",
    )

    anomaly = Anomaly(
        id="a1",
        name="Unexplained Fire",
        description_tags=["heat_source", "no_ignition_point"],
    )
    hyp = Hypothesis(
        id="h1",
        claim="spontaneous_combustion",
        testable_actions=["spectral_residue_analysis"],
        associated_clock_id="clock1",
    )
    anomaly.hypothesis_ids = ["h1"]
    world.anomalies["a1"] = anomaly.to_dict()
    world.hypotheses["h1"] = hyp.to_dict()

    return world


def test_build_scene_returns_scene_output():
    world = make_world()
    output = build_scene(world, "Lyra")
    assert isinstance(output, SceneOutput)


def test_scene_contains_location_info():
    world = make_world()
    output = build_scene(world, "Lyra")
    assert output.scene["location"] == "Workshop"
    assert "cluttered" in output.scene["description_tags"]


def test_scene_contains_evidence():
    world = make_world()
    output = build_scene(world, "Lyra")
    assert len(output.evidence) >= 1
    assert output.evidence[0]["id"] == "ev1"


def test_scene_contains_working_models():
    world = make_world()
    output = build_scene(world, "Lyra")
    assert len(output.working_models) >= 1
    wm = output.working_models[0]
    assert wm["anomaly_id"] == "a1"
    assert len(wm["hypotheses"]) >= 1


def test_scene_contains_clocks():
    world = make_world()
    output = build_scene(world, "Lyra")
    assert len(output.clocks) >= 1
    clock_names = [c["name"] for c in output.clocks]
    assert "Fire Risk" in clock_names


def test_scene_choices_count_in_range():
    world = make_world()
    output = build_scene(world, "Lyra")
    assert 3 <= len(output.choices) <= 5


def test_choices_are_choice_objects():
    world = make_world()
    output = build_scene(world, "Lyra")
    for choice in output.choices:
        assert isinstance(choice, Choice)
        assert isinstance(choice.description, str)
        assert isinstance(choice.position, str)
        assert isinstance(choice.estimated_effect, str)
        assert isinstance(choice.costs, dict)
        assert isinstance(choice.risks, list)


def test_scene_player_prompt_is_string():
    world = make_world()
    output = build_scene(world, "Lyra")
    assert isinstance(output.player_prompt, str)
    assert "Workshop" in output.player_prompt


def test_scene_player_prompt_contains_cost_tags():
    world = make_world()
    output = build_scene(world, "Lyra")
    assert "cost_physical:2" in output.player_prompt


def test_scene_player_prompt_no_prose():
    world = make_world()
    output = build_scene(world, "Lyra")
    # Prompt must be tag-only — no prose sentences (no ". " sentence boundary)
    assert ". " not in output.player_prompt
    # Must not end with a period followed by nothing (sentence terminator)
    assert not output.player_prompt.rstrip().endswith(".")


def test_scene_to_dict_has_all_required_keys():
    world = make_world()
    output = build_scene(world, "Lyra")
    d = output.to_dict()
    for key in ("scene", "evidence", "working_models", "clocks", "choices", "player_prompt"):
        assert key in d, f"Missing key: {key}"


def test_build_scene_unknown_player_raises():
    world = make_world()
    with pytest.raises(ValueError, match="not found"):
        build_scene(world, "Nobody")


def test_resolved_anomaly_not_in_working_models():
    world = make_world()
    world.anomalies["a1"]["resolved"] = True
    output = build_scene(world, "Lyra")
    for wm in output.working_models:
        assert wm["anomaly_id"] != "a1"
