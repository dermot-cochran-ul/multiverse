# The Grand Ensemble Multiverse (GEM) RPG based on the Evennia framwork

The Grand Ensemble Multiverse is a Quantum Multiverse, in accordance with the Many Worlds Interpretation of Qunantum Mechanics, in which each World is contained within the Cosmic 11-dimensional spacetime Bulk of M-Theory.

The physical universe is a four-dimensional spacetime, which can interact, gravitionaly, with other nearby spacetime regions, known as Etheric Universes. In some cases, super-strings, known as Etheric Strings may be attached at each end to two different Branes.

The gravitional influence of Etheric Strings and Etheric Universes, account for the missing "Dark Matter" and "Dark Energy" within the physical universe.

An Etheric Body is formed through the gravitional influence of a physical body. It may have consciousness and continue to exist, even after the destruction of the physical body around which it was formed.

---

## Interactive Fiction Engine (`engine/`)

A deterministic, dice-less, investigation-driven persistent sandbox engine. An LLM renders prose from structured scene state — the engine itself never produces prose.

### Architecture Principles

1. **Structured state is canonical.** Every scene produces a JSON structure (`SceneOutput`) containing `scene`, `evidence`, `working_models`, `clocks`, `choices`, and `player_prompt`. An LLM receives this to render prose; it cannot mutate game state.
2. **Stateless JSON API.** Every mutation is `(WorldState, Action) → (WorldState, SceneOutput)`. The FastAPI server holds no session state.
3. **No RNG.** Resolution uses `Position × Effect` lookup tables. Outcomes are deterministic given inputs.

### Package Layout

| Package | Role |
|---|---|
| `engine/consequence/` | `Clock` (0–6 segments, causal justification required), `Position × Effect` resolution table (pure dict lookup), cost domains |
| `engine/world/` | JSON-serializable `WorldState`, `Player`, `Location` dataclasses |
| `engine/investigation/` | `Anomaly` → `Evidence` → `Hypothesis` → testable actions that advance clocks. Instrumentation primitives |
| `engine/entities/` | `Nai` (clarity stabilizer), `CourtFae` (ambiguity predator), `GildedSaint` (virtue extractor) — each with deterministic `act(world_state)` producing measurable traces |
| `engine/clarity/` | `ClarityState` (0–10 score); explicit intent → clarity up; vague intent → Social/Psychological costs amplified |
| `engine/narrative/` | `build_scene()` produces `SceneOutput` JSON — the LLM contract boundary |
| `engine/persistence/` | JSON file snapshots (`data/snapshots/`), player reset with selective memory retention |
| `engine/api/` | Stateless FastAPI: `POST /action`, `GET /world/{id}`, `POST /world`, `POST /world/{id}/reset`, `GET /anomalies/{id}`, `POST /hypothesis/{id}` |
| `engine/monetization/` | `FeatureFlags` + `ServiceTier` stubs (no pay-to-win) |
| `engine/examples/` | `reactor_anomaly.py` — full demo scenario |

### Running the API

```bash
pip install -r requirements.txt
uvicorn engine.api.routes:app --reload
```

### Running Tests

```bash
pytest tests/
```

### Example Scenario

`engine/examples/reactor_anomaly.py` demonstrates:
- A world with a Reactor Chamber and a radiation anomaly
- Two competing hypotheses: containment micro-fracture vs etheric resonance bleed
- A player instrumentation action (radiation_dose) advances a clock, filling it
- The filled clock triggers new evidence being revealed
- Player reset retains anomaly discovery memory but clears costs and clarity

