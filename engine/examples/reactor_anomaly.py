"""Reactor anomaly demonstration scenario.

Shows:
1. A world with a 'Reactor Chamber' location containing a radiation anomaly.
2. Two competing hypotheses: 'containment_micro_fracture' vs 'etheric_resonance_bleed'.
3. A player takes an instrumentation action (radiation_dose) which advances
   the 'Containment Integrity' clock by 1 segment (position=Risky, effect=Standard).
4. The clock fills and triggers an event that reveals new evidence.
5. Player resets with memory retention of the anomaly discovery.
6. After reset, player still has the anomaly memory but clarity and costs are reset.
"""
from __future__ import annotations
import uuid

from engine.consequence.clocks import Clock
from engine.consequence.costs import CostDomain, apply_costs
from engine.consequence.resolution import Effect, Position, resolve
from engine.investigation.anomalies import Anomaly
from engine.investigation.evidence import Evidence
from engine.investigation.hypotheses import Hypothesis
from engine.investigation.instrumentation import Instrumentation
from engine.narrative.scene_builder import build_scene
from engine.persistence.storage import reset_player, save_world
from engine.world.state import Location, Player, WorldState


def run_scenario() -> dict:
    """Run the reactor anomaly scenario and return a summary dict."""

    # -----------------------------------------------------------------------
    # 1. Build world
    # -----------------------------------------------------------------------
    world = WorldState(world_id=f"reactor_{uuid.uuid4().hex[:8]}")

    reactor = Location(
        name="Reactor Chamber",
        description_tags=[
            "high_radiation",
            "containment_field_active",
            "sensor_noise",
            "pressure_drop",
        ],
        connections=["Control Room", "Maintenance Corridor"],
    )
    world.locations["Reactor Chamber"] = reactor

    player = Player(
        name="Investigator",
        location="Reactor Chamber",
        clarity_score=7.0,
    )
    world.players["Investigator"] = player

    # -----------------------------------------------------------------------
    # 2. Radiation anomaly with two competing hypotheses
    # -----------------------------------------------------------------------
    anomaly = Anomaly(
        id="anomaly_001",
        name="Reactor Radiation Anomaly",
        description_tags=[
            "radiation_spike",
            "unexplained_source",
            "containment_uncertain",
        ],
    )

    hyp_fracture = Hypothesis(
        id="hyp_fracture",
        claim="containment_micro_fracture",
        testable_actions=[
            "radiation_dose_measurement",
            "pressure_differential_check",
        ],
        associated_clock_id="containment_integrity",
    )

    hyp_etheric = Hypothesis(
        id="hyp_etheric",
        claim="etheric_resonance_bleed",
        testable_actions=["em_harmonics_scan", "spectral_residue_analysis"],
        associated_clock_id="etheric_bleed_clock",
    )

    anomaly.hypothesis_ids = ["hyp_fracture", "hyp_etheric"]
    world.anomalies["anomaly_001"] = anomaly.to_dict()
    world.hypotheses["hyp_fracture"] = hyp_fracture.to_dict()
    world.hypotheses["hyp_etheric"] = hyp_etheric.to_dict()

    # -----------------------------------------------------------------------
    # 3. Clocks
    # -----------------------------------------------------------------------
    containment_clock = Clock(
        name="Containment Integrity",
        segments=3,
        current=2,  # already at 2/3 — one more segment fills it
        trigger_effect="breach_imminent_evidence_revealed",
    )
    etheric_clock = Clock(
        name="Etheric Bleed",
        segments=4,
        current=0,
        trigger_effect="etheric_portal_opens",
    )
    world.clocks["containment_integrity"] = containment_clock
    world.clocks["etheric_bleed_clock"] = etheric_clock

    # -----------------------------------------------------------------------
    # 4. Player takes instrumentation action: radiation_dose measurement
    #    Position=Risky, Effect=Standard (per requirements)
    # -----------------------------------------------------------------------
    pos = Position.RISKY
    eff = Effect.STANDARD
    outcome = resolve(pos, eff)
    # outcome.clock_segments_advanced == 2; clock is at 2/3 so it fills

    justification = (
        "Player measured radiation_dose using instrumentation at Reactor Chamber"
    )
    filled = containment_clock.advance(outcome.clock_segments_advanced, justification)

    assert filled, "Containment Integrity clock should have filled."

    # -----------------------------------------------------------------------
    # 5. Clock fills → trigger effect: new evidence revealed
    # -----------------------------------------------------------------------
    new_evidence = Evidence(
        id="evidence_breach_sign",
        type="sensor_log",
        description_tags=[
            "micro_fracture_confirmed",
            "radiation_plume",
            "pressure_breach_sign",
        ],
        instrumentation_used=Instrumentation.RADIATION_DOSE,
    )
    world.evidence_store["evidence_breach_sign"] = new_evidence.to_dict()
    reactor.evidence_present.append("evidence_breach_sign")

    world.hypotheses["hyp_fracture"]["supporting_evidence"].append(
        "evidence_breach_sign"
    )

    world.flags["last_triggered_clock"] = "containment_integrity"
    world.flags["trigger_effect"] = containment_clock.trigger_effect

    # Apply costs of the risky action
    costs = {CostDomain.PHYSICAL: 1, CostDomain.INFORMATIONAL: 1}
    apply_costs(player, costs)
    player.memory["anomaly_discovery"] = {
        "anomaly_id": "anomaly_001",
        "name": "Reactor Radiation Anomaly",
        "clock_triggered": "containment_integrity",
        "evidence_found": ["evidence_breach_sign"],
    }

    scene_before = build_scene(world, "Investigator")
    save_world(world)

    # -----------------------------------------------------------------------
    # 6. Player reset with memory retention
    # -----------------------------------------------------------------------
    reset = reset_player(player, retain_memories=["anomaly_discovery"])

    assert reset.clarity_score == 5.0, "Clarity should be reset to 5.0"
    assert reset.cost_pools == {}, "Cost pools should be empty after reset"
    assert "anomaly_discovery" in reset.memory, "Anomaly memory should be retained"
    assert reset.memory["anomaly_discovery"]["anomaly_id"] == "anomaly_001"

    return {
        "scenario": "reactor_anomaly",
        "clock_filled": filled,
        "trigger_effect": world.flags.get("trigger_effect"),
        "evidence_revealed": ["evidence_breach_sign"],
        "player_costs_before_reset": {"physical": 1, "informational": 1},
        "player_after_reset": {
            "clarity": reset.clarity_score,
            "cost_pools": reset.cost_pools,
            "memory_keys": list(reset.memory.keys()),
        },
        "scene_fields": list(scene_before.to_dict().keys()),
    }


if __name__ == "__main__":
    import json
    result = run_scenario()
    print(json.dumps(result, indent=2))
