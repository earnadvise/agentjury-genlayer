# v0.3.0
# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }

import genlayer as gl
from genlayer.storage import TreeMap
import json

class AgentJury(gl.contract.Contract):
    """
    AgentJury: Autonomous Escrow & Arbitration Protocol for the Agentic Economy.
    Powered by GenLayer Intelligent Contracts, GenVM, and Optimistic Democracy.
    """
    bounties: TreeMap[str, str]
    bounty_count: str

    def __init__(self):
        self.bounty_count = "0"

    @gl.public.write
    def create_bounty(
        self,
        title: str,
        natural_language_spec: str,
        reward_amount: int
    ) -> int:
        new_count = int(self.bounty_count) + 1
        self.bounty_count = str(new_count)
        bounty_id = new_count

        bounty = {
            "id": bounty_id,
            "creator": str(gl.message.sender_address),
            "title": title,
            "spec": natural_language_spec,
            "reward": reward_amount,
            "worker": "",
            "deliverable_url": "",
            "summary": "",
            "status": "OPEN",
            "score": 0,
            "verdict_reasoning": "",
            "eval_count": 0
        }
        self.bounties[str(bounty_id)] = json.dumps(bounty)
        return bounty_id

    @gl.public.write
    def submit_deliverable(
        self,
        bounty_id: int,
        deliverable_url: str,
        summary: str
    ) -> bool:
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")
        
        bounty = json.loads(self.bounties[key])
        if bounty["status"] not in ["OPEN", "REJECTED"]:
            raise Exception("Bounty is not open for submission")

        bounty["worker"] = str(gl.message.sender_address)
        bounty["deliverable_url"] = deliverable_url
        bounty["summary"] = summary
        bounty["status"] = "SUBMITTED"
        self.bounties[key] = json.dumps(bounty)
        return True

    @gl.public.write
    def evaluate_and_settle(self, bounty_id: int) -> dict:
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")

        bounty = json.loads(self.bounties[key])
        if bounty["status"] != "SUBMITTED":
            raise Exception("Bounty has no submitted deliverable to evaluate")

        spec = bounty["spec"]
        url = bounty["deliverable_url"]
        summary = bounty["summary"]

        def nondet_review():
            deliverable_content = ""
            try:
                deliverable_content = gl.nondet.web.get(url)
            except Exception:
                deliverable_content = f"Deliverable Summary: {summary}"

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
            {{"passed": true, "score": 95, "reasoning": "concise explanation"}}
            """
            
            raw_response = gl.nondet.exec_prompt(prompt)
            clean_json = raw_response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)

        verdict = gl.eq_principle.strict_eq(nondet_review)

        bounty["score"] = int(verdict.get("score", 0))
        bounty["verdict_reasoning"] = str(verdict.get("reasoning", ""))
        bounty["eval_count"] += 1

        if verdict.get("passed", False):
            bounty["status"] = "SETTLED"
        else:
            bounty["status"] = "REJECTED"

        self.bounties[key] = json.dumps(bounty)
        return verdict

    @gl.public.view
    def get_bounty(self, bounty_id: int) -> str:
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")
        return self.bounties[key]

    @gl.public.view
    def list_bounties(self) -> str:
        all_bounties = []
        count = int(self.bounty_count)
        for i in range(1, count + 1):
            k = str(i)
            if k in self.bounties:
                all_bounties.append(json.loads(self.bounties[k]))
        return json.dumps(all_bounties)
