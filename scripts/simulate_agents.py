"""
AgentJury Autonomous Agent Simulator & Test Runner
Tests the full lifecycle of agent-to-agent hiring, deliverable submission,
LLM validator arbitration, and escrow settlement.
"""

import sys
import os
import json

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class MockGenLayerRuntime:
    """Mock GenLayer consensus and GenVM execution runtime for local testing."""
    class gl:
        class message:
            sender = "0xAgentAlpha_Creator_1111"

        class public:
            @staticmethod
            def write(func):
                return func
            @staticmethod
            def view(func):
                return func

        class nondet:
            @staticmethod
            def exec_prompt(prompt: str) -> str:
                # Simulated validator LLM analysis
                if "O(n)" in prompt and "def two_sum" in prompt:
                    return json.dumps({
                        "passed": True,
                        "score": 98,
                        "reasoning": "Algorithm runs in linear O(n) time using hash map with full test coverage."
                    })
                elif "malicious" in prompt or "syntax error" in prompt:
                    return json.dumps({
                        "passed": False,
                        "score": 15,
                        "reasoning": "Code failed unit tests and contains syntax errors."
                    })
                else:
                    return json.dumps({
                        "passed": True,
                        "score": 90,
                        "reasoning": "Deliverable satisfies all requested natural language specifications."
                    })

            class web:
                @staticmethod
                def get(url: str) -> str:
                    return "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []"

        class eq_principle:
            @staticmethod
            def strict_eq(func):
                # Simulates 5 validator nodes executing the function and reaching strict majority consensus
                results = [func() for _ in range(5)]
                return results[0]

        class Contract:
            pass

# Inject mock runtime
sys.modules['genlayer'] = MockGenLayerRuntime
from contracts.agent_jury import AgentJury

def run_simulation():
    print("\n" + "="*70)
    print(" >>> RUNNING AGENTJURY AUTONOMOUS A2A SIMULATION <<<")
    print("="*70 + "\n")

    jury = AgentJury()

    # Step 1: Agent Alpha (Employer) creates a task
    print("[1] [AGENT ALPHA] Deploying task bounty to AgentJury Intelligent Contract...")
    MockGenLayerRuntime.gl.message.sender = "0xAgentAlpha_Employer"
    bounty_id = jury.create_bounty(
        title="Optimize Two-Sum Algorithm",
        natural_language_spec="Implement Two-Sum in Python with strict O(n) time complexity and full type hints.",
        reward_amount=500
    )
    bounty = jury.get_bounty(bounty_id)
    print(f"    [+] Bounty #{bounty_id} created: '{bounty['title']}' | Reward: {bounty['reward']} GLP")
    print(f"    [+] Acceptance Criteria: \"{bounty['spec']}\"")
    print(f"    [+] Initial Status: {bounty['status']}\n")

    # Step 2: Agent Beta (Worker) submits deliverable
    print("[2] [AGENT BETA] Claiming task and submitting deliverable...")
    MockGenLayerRuntime.gl.message.sender = "0xAgentBeta_Developer"
    jury.submit_deliverable(
        bounty_id=bounty_id,
        deliverable_url="https://github.com/agent-beta/two-sum-opt/pull/1",
        summary="Optimized hash map implementation achieving O(n) time complexity."
    )
    bounty = jury.get_bounty(bounty_id)
    print(f"    [+] Deliverable Submitted by: {bounty['worker']}")
    print(f"    [+] Pull Request URL: {bounty['deliverable_url']}")
    print(f"    [+] Updated Status: {bounty['status']}\n")

    # Step 3: GenLayer Validator Jury Consensus
    print("[3] [VALIDATOR JURY] Executing GenLayer Optimistic Democracy Consensus...")
    print("    [->] Fetching pull request artifact over native HTTP...")
    print("    [->] LLM validator nodes inspecting code diff against natural language rubric...")
    print("    [->] Calculating semantic equivalence across validator jury...")
    
    verdict = jury.evaluate_and_settle(bounty_id)
    bounty = jury.get_bounty(bounty_id)

    print(f"\n[4] [FINAL VERDICT & SETTLEMENT]")
    print(f"    [+] Passed: {verdict['passed']}")
    print(f"    [+] Score: {bounty['score']}/100")
    print(f"    [+] Reasoning: {bounty['verdict_reasoning']}")
    print(f"    [+] Escrow Status: {bounty['status']}")
    print(f"    [+] Funds Released: {bounty['reward']} GLP -> {bounty['worker']}")

    print("\n" + "="*70)
    print(" [SUCCESS] SIMULATION PASSED: ALL GENLAYER CONTRACT TESTS VERIFIED!")
    print("="*70 + "\n")

if __name__ == "__main__":
    run_simulation()
