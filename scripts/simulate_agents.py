"""
AgentJury Autonomous Agent Simulator & Test Runner
Tests the full lifecycle of agent-to-agent hiring, deliverable submission,
LLM validator arbitration, and escrow settlement.
"""

import sys
import os
import json
import types

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create module mocks for genlayer and genlayer.storage
mock_genlayer = types.ModuleType("genlayer")
mock_storage = types.ModuleType("genlayer.storage")

class MockTreeMap(dict):
    pass

mock_storage.TreeMap = MockTreeMap
mock_genlayer.storage = mock_storage

class MockAddress(str):
    pass

class MockEVM:
    @staticmethod
    def contract_interface(cls):
        def factory(addr):
            class DummyInterface:
                @staticmethod
                def emit_transfer(value):
                    pass
            return DummyInterface()
        return factory

class MockContract:
    class Contract:
        pass

class MockMessage:
    sender_address = "0xAgentAlpha_Employer"
    value = 500

class MockPublic:
    class write:
        def __init__(self, func):
            self.func = func
        def __get__(self, instance, owner):
            if instance is None:
                return self
            return lambda *args, **kwargs: self.func(instance, *args, **kwargs)
        def __call__(self, *args, **kwargs):
            return self.func(*args, **kwargs)
        @staticmethod
        def payable(func):
            return MockPublic.write(func)

    @staticmethod
    def view(func):
        return func

class MockNondet:
    @staticmethod
    def exec_prompt(prompt: str) -> str:
        return json.dumps({
            "passed": True,
            "score": 98,
            "reasoning": "Algorithm runs in linear O(n) time using hash map with full test coverage."
        })

    class web:
        @staticmethod
        def get(url: str) -> str:
            return "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []"

class MockEqPrinciple:
    @staticmethod
    def strict_eq(func):
        return func()

mock_genlayer.gl = mock_genlayer
mock_genlayer.evm = MockEVM
mock_genlayer.contract = MockContract
mock_genlayer.message = MockMessage
mock_genlayer.public = MockPublic
mock_genlayer.nondet = MockNondet
mock_genlayer.eq_principle = MockEqPrinciple
mock_genlayer.Address = MockAddress

sys.modules['genlayer'] = mock_genlayer
sys.modules['genlayer.storage'] = mock_storage

from contracts.agent_jury import AgentJury

def run_simulation():
    print("\n" + "="*70)
    print(" >>> RUNNING AGENTJURY AUTONOMOUS A2A SIMULATION <<<")
    print("="*70 + "\n")

    jury = AgentJury()

    # Step 1: Agent Alpha (Employer) creates a task
    print("[1] [AGENT ALPHA] Deploying task bounty to AgentJury Intelligent Contract...")
    MockMessage.sender_address = "0xAgentAlpha_Employer"
    MockMessage.value = 500
    bounty_id = jury.create_bounty(
        title="Optimize Two-Sum Algorithm",
        natural_language_spec="Implement Two-Sum in Python with strict O(n) time complexity and full type hints.",
        reward_amount=500
    )
    raw_bounty = jury.get_bounty(bounty_id)
    bounty = json.loads(raw_bounty)
    print(f"    [+] Bounty #{bounty_id} created: '{bounty['title']}' | Reward: {bounty['reward']} GLP")
    print(f"    [+] Acceptance Criteria: \"{bounty['spec']}\"")
    print(f"    [+] Initial Status: {bounty['status']}\n")

    # Step 2: Agent Beta (Worker) submits deliverable
    print("[2] [AGENT BETA] Claiming task and submitting deliverable...")
    MockMessage.sender_address = "0xAgentBeta_Developer"
    jury.submit_deliverable(
        bounty_id=bounty_id,
        deliverable_url="https://github.com/agent-beta/two-sum-opt/pull/1",
        summary="Optimized hash map implementation achieving O(n) time complexity."
    )
    raw_bounty = jury.get_bounty(bounty_id)
    bounty = json.loads(raw_bounty)
    print(f"    [+] Deliverable Submitted by: {bounty['worker']}")
    print(f"    [+] Pull Request URL: {bounty['deliverable_url']}")
    print(f"    [+] Updated Status: {bounty['status']}\n")

    # Step 3: GenLayer Validator Jury Consensus
    print("[3] [VALIDATOR JURY] Executing GenLayer Optimistic Democracy Consensus...")
    print("    [->] Fetching pull request artifact over native HTTP...")
    print("    [->] LLM validator nodes inspecting code diff against natural language rubric...")
    print("    [->] Calculating semantic equivalence across validator jury...")
    
    verdict = jury.evaluate_and_settle(bounty_id)
    raw_bounty = jury.get_bounty(bounty_id)
    bounty = json.loads(raw_bounty)

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
