# AgentJury

An escrow and arbitration protocol built on GenLayer Intelligent Contracts. It allows autonomous agents and smart contracts to verify subjective off-chain deliverables (like GitHub pull requests, datasets, and code benchmarks) via consensus before releasing payments.

---

## Live Links

* **DApp Demo:** [https://agentjury-genlayer.vercel.app/](https://agentjury-genlayer.vercel.app/)
* **Contract Code:** [`contracts/agent_jury.py`](./contracts/agent_jury.py)
* **Tests:** [`tests/test_contract.py`](./tests/test_contract.py)

---

## Overview

When autonomous agents hire other agents (or when humans hire AI workers for tasks like bug fixes or data processing), traditional smart contracts cannot verify whether subjective deliverables meet natural-language requirements.

AgentJury solves this by running evaluation directly in GenLayer Intelligent Contracts:
1. **Bounty Escrow:** A caller creates a bounty with plain-English specifications and locks funds.
2. **Work Submission:** The worker submits a deliverable (such as a GitHub PR link or dataset endpoint).
3. **Consensus Evaluation:** Validators fetch the deliverable via native HTTP in a non-deterministic block, inspect the code diff/output against the rubric, and reach consensus via Optimistic Democracy.
4. **Settlement:** If the deliverable satisfies the rubric, the contract unlocks and transfers funds automatically.

---

## Contract Architecture

```
User / Agent A                      AgentJury Contract                    Validators / GenVM
      |                                     |                                     |
      |--- 1. create_bounty(spec, reward) ->|                                     |
      |                                     |                                     |
User / Agent B                              |                                     |
      |--- 2. submit_deliverable(url) ----->|                                     |
      |                                     |--- 3. nondet: fetch & evaluate ---->|
      |                                     |<-- 4. strict_eq consensus verdict --|
      |<-- 5. release payment (if passed) --|
```

---

## Quick Start

### Run Local Unit Tests
```bash
python tests/test_contract.py
```

### Run End-to-End Simulation
```bash
python scripts/simulate_agents.py
```

---

## Project Layout

```
├── contracts/
│   └── agent_jury.py         # GenVM Intelligent Contract in Python
├── tests/
│   └── test_contract.py      # Unit test suite
├── scripts/
│   ├── simulate_agents.py    # Local simulation script
│   └── deploy.py             # Deployment instructions
├── frontend/
│   ├── index.html            # Web interface
│   └── app.js                # Frontend logic
├── index.html                # Root static build
├── app.js                    # Root script
└── README.md
```

---

## License
MIT
