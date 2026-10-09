# v0.3.0
# { "Depends": "py-genlayer:5jycge4q8k23462jtb0b9fyey1s9qz928sz2nbrd9mg4sxqg2qng" }

import genlayer as gl
from genlayer.storage import TreeMap
import json

@gl.evm.contract_interface
class _Recipient:
    class View:
        pass
    class Write:
        pass

class AgentJury(gl.contract.Contract):
    """
    AgentJury: Autonomous Escrow & Arbitration Protocol for the Agentic Economy.
    Powered by GenLayer Intelligent Contracts, GenVM, and Optimistic Democracy.
    Enforces real native GEN deposits, strict web deliverable audits, and trustless payouts.
    """
    bounties: TreeMap[str, str]
    bounty_count: str

    def __init__(self):
        self.bounty_count = "0"
        try:
            self.bounties = TreeMap()
        except Exception:
            pass

    @gl.public.write.payable
    def create_bounty(
        self,
        title: str,
        natural_language_spec: str
    ) -> int:
        """
        Agent A creates a bounty and deposits real native GEN into escrow.
        Requires an actual nonzero GEN deposit attached to the transaction.
        """
        deposited = int(gl.message.value)
        if deposited <= 0:
            raise Exception("Bounty creation requires an actual nonzero GEN deposit in escrow")

        new_count = int(self.bounty_count) + 1
        self.bounty_count = str(new_count)
        bounty_id = new_count

        bounty = {
            "id": bounty_id,
            "creator": str(gl.message.sender_address),
            "title": title,
            "spec": natural_language_spec,
            "reward": deposited,
            "worker": "",
            "deliverable_url": "",
            "summary": "",
            "status": "OPEN", # OPEN, SUBMITTED, EVALUATED_PASSED, SETTLED, REJECTED, REFUND_PENDING, REFUNDED
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
        """
        Agent B submits the deliverable link (GitHub PR, raw code, or artifact URL).
        """
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
        """
        GenLayer validator jury executes the evaluation in consensus:
        1. Strictly fetches the live deliverable artifact via native HTTP in nondet.
        2. Fails immediately if the URL cannot be retrieved (no self-authored fallback).
        3. LLM validators inspect the retrieved artifact against the natural language spec.
        4. Reaches consensus using Optimistic Democracy (strict semantic equivalence).
        5. Executes on-chain token settlement only upon successful transfer; failures remain retriable.
        """
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")

        bounty = json.loads(self.bounties[key])
        if bounty["status"] not in ["SUBMITTED", "EVALUATED_PASSED"]:
            raise Exception("Bounty has no submitted deliverable to evaluate or settle")

        # If already evaluated as passed in a previous round, retry transfer directly
        if bounty["status"] == "EVALUATED_PASSED":
            try:
                _Recipient(gl.Address(bounty["worker"])).emit_transfer(value=int(bounty["reward"]))
                bounty["status"] = "SETTLED"
                self.bounties[key] = json.dumps(bounty)
                return {"passed": True, "score": bounty["score"], "reasoning": "Settlement transfer completed successfully."}
            except Exception as e:
                bounty["status"] = "EVALUATED_PASSED"
                self.bounties[key] = json.dumps(bounty)
                raise Exception(f"Payout transfer failed; remains retriable: {str(e)}")

        spec = bounty["spec"]
        url = bounty["deliverable_url"]

        # Non-deterministic block for native web fetching and independent LLM review
        def nondet_review():
            deliverable_content = ""
            try:
                response = gl.nondet.web.get(url)
                if not response or len(response.strip()) == 0:
                    return {
                        "passed": False,
                        "score": 0,
                        "reasoning": "Verification failed: Empty response received from deliverable URL."
                    }
                deliverable_content = response[:4000]
            except Exception as e:
                return {
                    "passed": False,
                    "score": 0,
                    "reasoning": f"Verification failed: Deliverable URL unreachable or invalid ({str(e)})."
                }

            prompt = f"""
            You are an impartial, strict technical auditor for an on-chain smart contract escrow.
            
            CONTRACT ACCEPTANCE CRITERIA:
            {spec}
            
            DELIVERABLE ARTIFACT CONTENT (Retrieved live from {url}):
            {deliverable_content}
            
            OBJECTIVE:
            Evaluate whether the retrieved deliverable content objectively fulfills the acceptance criteria.
            Do not assume or accept unverified claims.
            
            Respond strictly in valid JSON format with NO markdown formatting:
            {{"passed": true, "score": 95, "reasoning": "concise explanation"}}
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
            # Attempt transfer; only mark SETTLED if transfer succeeds
            try:
                _Recipient(gl.Address(bounty["worker"])).emit_transfer(value=int(bounty["reward"]))
                bounty["status"] = "SETTLED"
            except Exception as e:
                # Keep state as EVALUATED_PASSED so settlement remains retriable
                bounty["status"] = "EVALUATED_PASSED"
                self.bounties[key] = json.dumps(bounty)
                raise Exception(f"Evaluation passed ({bounty['score']}/100) but transfer failed; remains retriable: {str(e)}")
        else:
            bounty["status"] = "REJECTED"

        self.bounties[key] = json.dumps(bounty)
        return verdict

    @gl.public.write
    def retry_payout(self, bounty_id: int) -> bool:
        """
        Retries settlement payout for a bounty that passed evaluation but whose transfer failed.
        """
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")

        bounty = json.loads(self.bounties[key])
        if bounty["status"] != "EVALUATED_PASSED":
            raise Exception("Bounty is not pending settlement retry")

        try:
            _Recipient(gl.Address(bounty["worker"])).emit_transfer(value=int(bounty["reward"]))
            bounty["status"] = "SETTLED"
            self.bounties[key] = json.dumps(bounty)
            return True
        except Exception as e:
            bounty["status"] = "EVALUATED_PASSED"
            self.bounties[key] = json.dumps(bounty)
            raise Exception(f"Payout transfer retry failed: {str(e)}")

    @gl.public.write
    def refund_bounty(self, bounty_id: int) -> bool:
        """
        Allows the creator to reclaim escrowed funds if a bounty was rejected
        or if an open bounty is cancelled before submission.
        Only marks REFUNDED upon successful transfer; failures remain retriable.
        """
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")

        bounty = json.loads(self.bounties[key])
        sender = str(gl.message.sender_address)

        if sender != bounty["creator"]:
            raise Exception("Only the bounty creator can request a refund")

        if bounty["status"] not in ["OPEN", "REJECTED", "REFUND_PENDING"]:
            raise Exception("Bounty cannot be refunded in current status")

        reward_val = int(bounty["reward"])
        if reward_val <= 0:
            bounty["status"] = "REFUNDED"
            self.bounties[key] = json.dumps(bounty)
            return True

        # Perform transfer first; only mark REFUNDED on success
        try:
            _Recipient(gl.Address(bounty["creator"])).emit_transfer(value=reward_val)
            bounty["status"] = "REFUNDED"
            self.bounties[key] = json.dumps(bounty)
            return True
        except Exception as e:
            bounty["status"] = "REFUND_PENDING"
            self.bounties[key] = json.dumps(bounty)
            raise Exception(f"Refund transfer failed, remains retriable: {str(e)}")

    @gl.public.view
    def get_bounty(self, bounty_id: int) -> str:
        """View details of a specific bounty as JSON string."""
        key = str(bounty_id)
        if key not in self.bounties:
            raise Exception("Bounty not found")
        return self.bounties[key]

    @gl.public.view
    def list_bounties(self) -> str:
        """List all active and historical bounties as JSON array string."""
        all_bounties = []
        count = int(self.bounty_count)
        for i in range(1, count + 1):
            k = str(i)
            if k in self.bounties:
                all_bounties.append(json.loads(self.bounties[k]))
        return json.dumps(all_bounties)
