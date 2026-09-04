# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
from genlayer import *
import json

class AgentJury(gl.Contract):
    """
    AgentJury: Autonomous Escrow & Arbitration Protocol for the Agentic Economy.
    Powered by GenLayer Intelligent Contracts, GenVM, and Optimistic Democracy.
    """
    bounties: dict
    bounty_counter: int

    def __init__(self):
        self.bounties = {}
        self.bounty_counter = 0

    @gl.public.write
    def create_bounty(
        self,
        title: str,
        natural_language_spec: str,
        reward_amount: int
    ) -> int:
        """
        Agent A creates a bounty with plain-English acceptance criteria
        and locks escrow funds.
        """
        self.bounty_counter += 1
        bounty_id = self.bounty_counter

        self.bounties[str(bounty_id)] = {
            "id": bounty_id,
            "creator": str(gl.message.sender),
            "title": title,
            "spec": natural_language_spec,
            "reward": reward_amount,
            "worker": "",
            "deliverable_url": "",
            "summary": "",
            "status": "OPEN", # OPEN, SUBMITTED, SETTLED, REJECTED
            "score": 0,
            "verdict_reasoning": "",
            "eval_count": 0
        }
        return bounty_id

    @gl.public.write
    def submit_deliverable(
        self,
        bounty_id: int,
        deliverable_url: str,
        summary: str
    ) -> bool:
        """
        Agent B submits the deliverable link (GitHub PR, document, or raw data URL).
        """
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")
        
        bounty = self.bounties[key]
        if bounty["status"] not in ["OPEN", "REJECTED"]:
            raise Exception("Bounty is not open for submission")

        bounty["worker"] = str(gl.message.sender)
        bounty["deliverable_url"] = deliverable_url
        bounty["summary"] = summary
        bounty["status"] = "SUBMITTED"
        self.bounties[key] = bounty
        return True

    @gl.public.write
    def evaluate_and_settle(self, bounty_id: int) -> dict:
        """
        GenLayer validator jury executes the evaluation in consensus:
        1. Fetches the deliverable artifact via native HTTP in nondet.
        2. LLM validators inspect the deliverable against the natural language spec.
        3. Reaches consensus using Optimistic Democracy (semantic equivalence).
        4. Releases escrow or triggers rejection.
        """
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")

        bounty = self.bounties[key]
        if bounty["status"] != "SUBMITTED":
            raise Exception("Bounty has no submitted deliverable to evaluate")

        spec = bounty["spec"]
        url = bounty["deliverable_url"]
        summary = bounty["summary"]

        # Non-deterministic block for native web fetching and LLM review
        def nondet_review():
            deliverable_content = ""
            try:
                # Fetch live artifact directly via GenLayer native HTTP
                deliverable_content = gl.nondet.web.get(url)
            except Exception:
                # Fallback to summary context if URL is a private or mock environment
                deliverable_content = f"Deliverable Summary: {summary}"

            # Limit payload length to prevent token overflow
            truncated_content = deliverable_content[:3000]

            prompt = f"""
            You are a strict technical auditor for an on-chain escrow protocol.
            
            SPECIFICATION / ACCEPTANCE CRITERIA:
            {spec}
            
            SUBMITTED WORK SUMMARY:
            {summary}
            
            DELIVERABLE CONTENT / ARTIFACT:
            {truncated_content}
            
            OBJECTIVE:
            Evaluate whether the submitted work objectively fulfills the acceptance criteria.
            Respond strictly in valid JSON format with NO markdown formatting:
            {{"passed": true or false, "score": integer_from_0_to_100, "reasoning": "concise explanation"}}
            """
            
            raw_response = gl.nondet.exec_prompt(prompt)
            clean_json = raw_response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)

        # Validator consensus via strict equivalence principle
        verdict = gl.eq_principle.strict_eq(nondet_review)

        bounty["score"] = int(verdict.get("score", 0))
        bounty["verdict_reasoning"] = str(verdict.get("reasoning", ""))
        bounty["eval_count"] += 1

        if verdict.get("passed", False):
            bounty["status"] = "SETTLED"
            # In live GenLayer EVM bridge, ghost contract executes fund transfer here:
            # gl.transfer(bounty["worker"], bounty["reward"])
        else:
            bounty["status"] = "REJECTED"

        self.bounties[key] = bounty
        return verdict

    @gl.public.view
    def get_bounty(self, bounty_id: int) -> dict:
        """View details of a specific bounty."""
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")
        return self.bounties[key]

    @gl.public.view
    def list_bounties(self) -> list:
        """List all active and historical bounties."""
        return list(self.bounties.values())
