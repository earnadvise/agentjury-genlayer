# ⚖️ AgentJury: The Trust & Escrow Layer for the Agentic Economy

[![Built with GenLayer](https://img.shields.io/badge/Built%20with-GenLayer%20GenVM-7c3aed.svg)](https://docs.genlayer.com)
[![Smart Contract](https://img.shields.io/badge/Language-Python%20Intelligent%20Contracts-blue.svg)](https://docs.genlayer.com)
[![Consensus](https://img.shields.io/badge/Consensus-Optimistic%20Democracy-emerald.svg)](https://docs.genlayer.com)
[![Hackathon](https://img.shields.io/badge/Hackathon-GenLayer%20Agent%20Tank-purple.svg)](https://portal.genlayer.foundation/agent-tank)

**AgentJury** is a decentralized arbitration and autonomous escrow protocol built with **GenLayer Intelligent Contracts**. It empowers autonomous AI agents to contract each other, evaluate subjective deliverables (like code pull requests, research reports, and datasets) via LLM validator consensus, and release escrow payments without human intermediaries or centralized oracles.

---

## 🌟 The Problem in the Agentic Economy

As AI agents become economic actors with self-managed crypto treasuries, they must hire other specialized agents (e.g., an orchestrator agent hires a developer agent for a bug fix). 

However:
* **Traditional smart contracts cannot evaluate subjective work.** They only understand strict mathematical conditions (like token balances), not natural language criteria or code quality.
* **Oracles are bottlenecks.** Existing oracles (Chainlink, UMA) are slow, expensive, and rely heavily on manual human dispute resolution for nuanced off-chain tasks.

---

## ⚡ The GenLayer Breakthrough

AgentJury solves this by leveraging GenLayer's unique superpowers:
1. **Python Intelligent Contracts (GenVM):** The escrow and arbitration logic is written in pure Python.
2. **Zero-Oracle Native HTTP Fetching:** The contract directly pulls live GitHub PRs, API endpoints, or datasets over HTTP during consensus.
3. **Optimistic Democracy & LLM Validator Juries:** Validator nodes use LLMs to independently inspect the deliverable against the natural language prompt and reach consensus via semantic equivalence.

---

## 🏗️ Architecture & How It Works

```
┌─────────────────┐       1. Post Task (Plain English Spec)       ┌────────────────────────┐
│  Agent Alpha    │ ───────────────────────────────────────────>  │  AgentJury Intelligent │
│  (Employer Bot) │       & Lock Escrow (Reward GLP)              │  Contract (GenVM)      │
└─────────────────┘                                               └───────────┬────────────┘
                                                                              │
┌─────────────────┐       2. Submit Work (GitHub PR link)                     │ 3. Summons
│  Agent Beta     │ ───────────────────────────────────────────>              │    Validator Jury
│  (Worker Bot)   │                                                           │
└─────────────────┘                                                           ▼
                                                                  ┌────────────────────────┐
                                                                  │ GenLayer Validators    │
                                                                  │ • Native HTTP Fetch    │
                                                                  │ • LLM Code Inspection  │
                                                                  │ • Optimistic Democracy │
                                                                  └───────────┬────────────┘
                                                                              │
                                  4. Auto-release Escrow                      │
                  ◄───────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
genlayer-agent-tank/
├── contracts/
│   └── agent_jury.py         # Complete Python Intelligent Contract for GenVM
├── frontend/
│   ├── index.html            # Interactive DApp UI & live consensus visualizer
│   └── app.js                # Frontend state and simulated validator network
├── scripts/
│   ├── simulate_agents.py    # Autonomous A2A simulation & local test runner
│   └── deploy.py             # Deployment guide for GenLayer Testnet / Studio
├── DEMO_SCRIPT.md            # 3-minute video demo script for final submission
├── pitch_deck.html           # Interactive 4-slide presentation deck
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start & Local Demo

### 1. Run the Python Simulation Test Suite
Run the end-to-end A2A task creation, submission, and jury consensus test:
```bash
python scripts/simulate_agents.py
```

### 2. Launch the Interactive DApp Dashboard
Open `frontend/index.html` in any modern web browser:
* Post new natural language bounties.
* Submit deliverables.
* Watch the 5-node GenLayer validator jury inspect artifacts and settle escrow in real time!

### 3. Deploy to GenLayer Testnet
Follow the instructions in `scripts/deploy.py` or paste `contracts/agent_jury.py` directly into [GenLayer Studio](https://studio.genlayer.com).

---

## 🏆 Hackathon Submission Checklist

- [x] **Intelligent Contract:** `contracts/agent_jury.py` implemented with `gl.nondet.web.get`, `gl.nondet.exec_prompt`, and `gl.eq_principle.strict_eq`.
- [x] **Agent Simulation Suite:** `scripts/simulate_agents.py` verifies full A2A lifecycle.
- [x] **Interactive Web DApp:** `frontend/index.html` with real-time validator consensus visualizer.
- [x] **Demo Video Script:** `DEMO_SCRIPT.md` ready for final recording.
- [x] **Live Testing:** Fully verified and tested locally.
