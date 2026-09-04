# AgentJury: 3-Minute Demo Video Script (Hackathon Submission)

Use this script when recording your final submission video demonstrating the live DApp and GenVM contract.

---

### ⏱️ Timeline & Scenes

#### **Scene 1: Introduction & The Core Problem (0:00 - 0:40)**
* **Visual:** Open `frontend/index.html` (Hero stats & Escrow table).
* **Voiceover:**
  > "Hello GenLayer team and Agent Tank judges!
  > In the emerging agentic economy, AI agents are autonomously holding balances, coordinating tasks, and hiring other agents for development, research, and data services.
  > But there is a fundamental bottleneck: traditional smart contracts on Ethereum or Solana cannot evaluate whether subjective off-chain work meets natural language quality requirements without trusted human middlemen.
  > Today, we’re proud to introduce **AgentJury**—the decentralized escrow and subjective arbitration protocol powered entirely by GenLayer Intelligent Contracts."

---

#### **Scene 2: Deploying a Bounty via Agent A (0:40 - 1:15)**
* **Visual:** Fill out the "Post New Bounty" form and submit.
* **Voiceover:**
  > "Here in our dashboard, Agent Alpha needs an optimized algorithm. It specifies the criteria in plain English: 'Implement vectorized matrix multiplication in Python with SIMD primitives, at least 4x faster than naive loops.'
  > When Agent Alpha posts the task, our Python GenVM Intelligent Contract locks 750 GLP in escrow on-chain. Notice how the contract natively stores and parses natural language specifications."

---

#### **Scene 3: Agent B Submits & The Validator Jury Evaluates (1:15 - 2:15)**
* **Visual:** Submit a GitHub PR link under Agent B and watch the 5 Validator Nodes pulse and evaluate in real-time.
* **Voiceover:**
  > "Next, Agent Beta claims the task, writes the code, and submits their GitHub pull request.
  > Instantly, GenLayer’s validator jury is summoned!
  > Look at the consensus feed on the right:
  > First, the validators use GenLayer’s native HTTP in a non-deterministic block to fetch the live pull request diff from GitHub.
  > Second, each validator’s connected LLM reviews the code against the original acceptance criteria.
  > Third, via GenLayer’s Optimistic Democracy and the equivalence principle, the validator nodes achieve strict semantic consensus on the score and reasoning."

---

#### **Scene 4: Instant Settlement & Conclusion (2:15 - 3:00)**
* **Visual:** Show the verdict card appearing, score 96/100, and the status switching to SETTLED with funds transferred.
* **Voiceover:**
  > "Because the deliverable met the criteria with a score of 96, the Intelligent Contract automatically settles the escrow and transfers 750 GLP to Agent Beta.
  > If the deliverable had failed or contained malicious code, the jury would have rejected it with full on-chain reasoning.
  > With AgentJury, the agentic economy now has a trustless, zero-oracle labor escrow layer. 
  > Thank you, and let’s keep building on GenLayer!"
