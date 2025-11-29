# Project Eris: The Chaos Engineering Module for Raptorflow

## Overview
**"Order is easy. Chaos is the true test."**

Project Eris introduces a new "Lord" to the Council: **Eris, the Lady of Discord**. Unlike other agents who strive for optimization and alignment, Eris's role is to **stress-test** the strategies designed by the Architect and Strategos. She introduces controlled entropy—market crashes, viral scandals, competitor disruptions—to ensure the developed strategies are resilient, not just optimal under ideal conditions.

## The "Surprise" Feature
Turn your static marketing planner into a dynamic **Wargaming Simulator**.

## Architectural Design

### 1. New Agent: Eris Lord (`backend/agents/council_of_lords/eris.py`)
- **Role**: Adversary / Red Teamer
- **Capabilities**:
    - `inject_entropy`: Modify active context with negative or disruptive variables.
    - `summon_black_swan`: Generate a high-impact, low-probability event (e.g., "Global platform outage", "Regulatory crackdown").
    - `devil's_advocate`: Analyze a strategy and generate a counter-argument or "pre-mortem".

### 2. New Data Models (`backend/models/chaos.py`)
- `ChaosEvent`: Represents a disruption (Type: `market`, `reputation`, `technical`, `legal`).
- `ResilienceScore`: A metric (0-100) calculated based on how well a strategy survives Eris's simulations.

### 3. Integration Points
- **RaptorBus Interception**: Eris can intercept messages between Lords. For example, she might intercept a "Trend Report" from Seer and inject noise before it reaches Strategos, simulating "fog of war".
- **Simulation Loop**: A new `POST /api/simulation/wargame` endpoint that runs the current strategy against an Eris scenario.

### 4. Frontend Experience (`src/pages/strategy/ErisDashboard.tsx`)
- **"The Red Button"**: A distinctive UI element to activate Wargame Mode.
- **Chaos Logs**: A terminal-style feed showing Eris's injections (e.g., *"Eris injected: Competitor X just launched a clone feature at 50% price"*).
- **Survival Rating**: A final score showing how robust the strategy is.

## Implementation Steps

### Phase 1: The Summoning (Backend)
1.  Define `ChaosEvent` schema.
2.  Implement `ErisLord` class inheriting from `LordAgent`.
3.  Register Eris in the `AgentRegistry`.

### Phase 2: The Discord (Logic)
1.  Implement `generate_scenario` capability using LLM (prompted to be creative and ruthless).
2.  Create the "Resilience Scoring" logic: Strategy success probability * (1 - Impact of Chaos Event).

### Phase 3: The Arena (Frontend)
1.  Create the "Wargame" view in the Strategy section.
2.  Visualize the "Battle" between the Strategy and the Chaos Events.

## Why This Fits Raptorflow
Raptorflow is about high-end, intelligent automation. True intelligence requires adaptability. By adding an adversarial component, we move from "Planning" to "Antifragility". Eris makes the entire system smarter by forcing it to defend its decisions.
