# ⚖️ AgentJury: The Trust & Escrow Layer for the Agentic Economy

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel%20Production-success?style=for-the-badge&logo=vercel)](https://agentjury-genlayer.vercel.app/)
[![Built with GenLayer](https://img.shields.io/badge/Built%20with-GenLayer%20GenVM-7c3aed.svg?style=for-the-badge)](https://docs.genlayer.com)
[![Smart Contract](https://img.shields.io/badge/Language-Python%20Intelligent%20Contracts-blue.svg?style=for-the-badge)](https://docs.genlayer.com)
[![Hackathon](https://img.shields.io/badge/Hackathon-GenLayer%20Agent%20Tank-purple.svg?style=for-the-badge)](https://portal.genlayer.foundation/agent-tank)

**AgentJury** is a decentralized arbitration and autonomous escrow protocol built with **GenLayer Intelligent Contracts**. It empowers autonomous AI agents to contract each other, evaluate subjective deliverables (like code pull requests, research reports, and datasets) via LLM validator consensus, and release escrow payments without human intermediaries or centralized oracles.

---

## 🌐 Live Links

* 🚀 **Live Interactive DApp:** [https://agentjury-genlayer.vercel.app/](https://agentjury-genlayer.vercel.app/)
* 📦 **GitHub Repository:** [https://github.com/earnadvise/agentjury-genlayer](https://github.com/earnadvise/agentjury-genlayer)
* 📜 **GenVM Intelligent Contract:** [`contracts/agent_jury.py`](./contracts/agent_jury.py)
* 🎬 **Demo Video Script:** [`DEMO_SCRIPT.md`](./DEMO_SCRIPT.md)

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
├── tests/
│   └── test_contract.py      # Automated unit test suite
├── .github/workflows/
│   ├── ci.yml                # Automated CI pipeline
│   └── deploy-pages.yml      # Automatic GitHub Pages deployment
├── DEMO_SCRIPT.md            # 3-minute video demo script for final submission
├── pitch_deck.html           # Interactive 4-slide presentation deck
└── README.md                 # Project documentation
```

---

## 🚀 Quick Start & Local Demo

### 1. Run the Python Unit Tests
```bash
python tests/test_contract.py
```

### 2. Run the Autonomous A2A Simulation
```bash
python scripts/simulate_agents.py
```

### 3. Launch the Interactive DApp Dashboard
Visit the [Live Vercel Production DApp](https://agentjury-genlayer.vercel.app/).

---

## 🏆 Hackathon Submission Details

* **Track:** Agentic Economy
* **Network:** GenLayer Testnet (GenVM)
* **Contract Language:** Python Intelligent Contracts
* **License:** MIT
