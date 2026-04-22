"""Tests for the investigation system."""
from engine.investigation.anomalies import Anomaly
from engine.investigation.evidence import Evidence
from engine.investigation.hypotheses import Hypothesis
from engine.investigation.instrumentation import Instrumentation
from engine.consequence.clocks import Clock
from engine.world.state import WorldState, Location


def make_world() -> WorldState:
    world = WorldState(world_id="inv_test")
    world.locations["Lab"] = Location(name="Lab", description_tags=["sterile"])
    return world


def test_create_anomaly():
    anomaly = Anomaly(
        id="a1",
        name="Signal Distortion",
        description_tags=["em_spike", "unexplained"],
    )
    assert anomaly.id == "a1"
    assert not anomaly.resolved
    assert "em_spike" in anomaly.description_tags


def test_add_evidence_to_anomaly():
    anomaly = Anomaly(id="a1", name="Signal Distortion")
    ev = Evidence(
        id="ev1",
        type="sensor_log",
        description_tags=["em_spike"],
        instrumentation_used=Instrumentation.EM_HARMONICS,
    )
    anomaly.evidence_ids.append(ev.id)
    assert "ev1" in anomaly.evidence_ids


def test_associate_hypothesis_with_anomaly():
    anomaly = Anomaly(id="a1", name="Signal Distortion")
    hyp = Hypothesis(
        id="h1",
        claim="resonance_bleed",
        testable_actions=["em_harmonics_scan"],
        associated_clock_id="clock_em",
    )
    anomaly.hypothesis_ids.append(hyp.id)
    assert "h1" in anomaly.hypothesis_ids
    assert hyp.associated_clock_id == "clock_em"


def test_hypothesis_testable_action_advances_correct_clock():
    world = make_world()

    clock = Clock(name="EM Clock", segments=3, current=0)
    world.clocks["clock_em"] = clock

    anomaly = Anomaly(id="a1", name="Signal Distortion")
    hyp = Hypothesis(
        id="h1",
        claim="resonance_bleed",
        testable_actions=["em_harmonics_scan"],
        associated_clock_id="clock_em",
    )
    anomaly.hypothesis_ids.append("h1")
    world.anomalies["a1"] = anomaly.to_dict()
    world.hypotheses["h1"] = hyp.to_dict()

    # Simulate: player tests hypothesis -> advance associated clock
    associated_id = world.hypotheses["h1"]["associated_clock_id"]
    assert associated_id == "clock_em"
    filled = world.clocks[associated_id].advance(1, "EM harmonics scan performed.")
    assert world.clocks["clock_em"].current == 1
    assert not filled


def test_anomaly_resolved_flag():
    anomaly = Anomaly(id="a1", name="Signal Distortion")
    assert not anomaly.resolved
    anomaly.resolved = True
    assert anomaly.resolved


def test_evidence_serialization_roundtrip():
    ev = Evidence(
        id="ev1",
        type="residue",
        description_tags=["radiation_trace"],
        instrumentation_used=Instrumentation.RADIATION_DOSE,
    )
    d = ev.to_dict()
    restored = Evidence.from_dict(d)
    assert restored.id == ev.id
    assert restored.type == ev.type
    assert restored.instrumentation_used == Instrumentation.RADIATION_DOSE


def test_hypothesis_serialization_roundtrip():
    hyp = Hypothesis(
        id="h1",
        claim="test_claim",
        supporting_evidence=["ev1"],
        testable_actions=["action_a"],
        associated_clock_id="clk1",
    )
    d = hyp.to_dict()
    restored = Hypothesis.from_dict(d)
    assert restored.id == hyp.id
    assert restored.claim == hyp.claim
    assert restored.supporting_evidence == ["ev1"]
    assert restored.associated_clock_id == "clk1"


def test_anomaly_serialization_roundtrip():
    anomaly = Anomaly(
        id="a1",
        name="Test Anomaly",
        description_tags=["tag1"],
        evidence_ids=["ev1"],
        hypothesis_ids=["h1"],
        resolved=False,
    )
    d = anomaly.to_dict()
    restored = Anomaly.from_dict(d)
    assert restored.id == anomaly.id
    assert restored.name == anomaly.name
    assert restored.evidence_ids == ["ev1"]
    assert restored.hypothesis_ids == ["h1"]
    assert not restored.resolved


def test_all_instrumentation_types_exist():
    expected = {
        "timing_jitter",
        "em_harmonics",
        "radiation_dose",
        "spectral_residue",
        "gravitational_flux",
    }
    actual = {i.value for i in Instrumentation}
    assert actual == expected
