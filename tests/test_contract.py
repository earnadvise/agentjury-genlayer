"""
AgentJury Contract Test Suite
Covers:
1. Zero deposit rejection on bounty creation (gl.message.value <= 0)
2. Nonzero deposit acceptance and escrow recording
3. Deliverable submission by workers
4. Automated LLM consensus evaluation
5. Settlement transfer success (SETTLED)
6. Settlement transfer failure handling (EVALUATED_PASSED retriable state)
7. Retry payout execution (retry_payout -> SETTLED)
8. Strict evaluation failure on invalid / 404 deliverables (REJECTED)
9. Refund transfer success (REFUNDED)
10. Refund transfer failure handling (REFUND_PENDING retriable state)
11. Retry refund execution (refund_bounty -> REFUNDED)
12. Unauthorized refund rejection
"""

import sys
import os
import json
import unittest
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

class MockEVMState:
    should_fail_transfer = False

class MockEVM:
    @staticmethod
    def contract_interface(cls):
        def factory(addr):
            class DummyInterface:
                @staticmethod
                def emit_transfer(value):
                    if MockEVMState.should_fail_transfer:
                        raise Exception("Simulated EVM transfer execution failure (network timeout / out of gas)")
                    return True
            return DummyInterface()
        return factory

class MockContract:
    class Contract:
        pass

class MockMessage:
    sender_address = "0xAgentAlpha_Creator"
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
        if "FAIL_TEST" in prompt or "404" in prompt or "invalid" in prompt:
            return json.dumps({
                "passed": False,
                "score": 15,
                "reasoning": "Deliverable failed to fulfill acceptance criteria."
            })
        return json.dumps({
            "passed": True,
            "score": 95,
            "reasoning": "Criteria fully satisfied and verified."
        })

    class web:
        @staticmethod
        def get(url: str) -> str:
            if "404" in url or "invalid" in url:
                raise Exception("HTTP 404 Not Found")
            return "def solution(): return True"

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

class TestAgentJury(unittest.TestCase):
    def setUp(self):
        MockEVMState.should_fail_transfer = False
        MockMessage.sender_address = "0xAgentAlpha_Creator"
        MockMessage.value = 500

    def test_create_bounty_zero_deposit_fails(self):
        """Zero deposit must be rejected with an exception."""
        jury = AgentJury()
        MockMessage.value = 0
        with self.assertRaises(Exception) as ctx:
            jury.create_bounty("Task Zero", "Spec Zero")
        self.assertIn("nonzero GEN deposit", str(ctx.exception))

    def test_create_bounty_negative_deposit_fails(self):
        """Negative deposit must be rejected with an exception."""
        jury = AgentJury()
        MockMessage.value = -10
        with self.assertRaises(Exception) as ctx:
            jury.create_bounty("Task Negative", "Spec Negative")
        self.assertIn("nonzero GEN deposit", str(ctx.exception))

    def test_create_bounty_nonzero_deposit_success(self):
        """Nonzero deposit records bounty with reward matched to gl.message.value."""
        jury = AgentJury()
        MockMessage.value = 750
        bounty_id = jury.create_bounty("Task Nonzero", "Spec Nonzero")
        self.assertEqual(bounty_id, 1)

        raw_bounty = jury.get_bounty(1)
        bounty = json.loads(raw_bounty)
        self.assertEqual(bounty["reward"], 750)
        self.assertEqual(bounty["status"], "OPEN")
        self.assertEqual(bounty["creator"], "0xAgentAlpha_Creator")

    def test_submit_deliverable(self):
        """Worker submits deliverable and updates status to SUBMITTED."""
        jury = AgentJury()
        jury.create_bounty("Task B", "Spec B")
        MockMessage.sender_address = "0xWorkerAgent"
        success = jury.submit_deliverable(1, "https://github.com/test/pr/1", "Done")
        self.assertTrue(success)

        bounty = json.loads(jury.get_bounty(1))
        self.assertEqual(bounty["status"], "SUBMITTED")
        self.assertEqual(bounty["worker"], "0xWorkerAgent")
        self.assertEqual(bounty["deliverable_url"], "https://github.com/test/pr/1")

    def test_evaluate_and_settle_success(self):
        """Successful evaluation and payout transfer marks bounty SETTLED."""
        jury = AgentJury()
        jury.create_bounty("Task C", "Spec C")
        MockMessage.sender_address = "0xWorkerAgent"
        jury.submit_deliverable(1, "https://github.com/test/pr/1", "Done")

        verdict = jury.evaluate_and_settle(1)
        self.assertTrue(verdict["passed"])
        self.assertEqual(verdict["score"], 95)

        bounty = json.loads(jury.get_bounty(1))
        self.assertEqual(bounty["status"], "SETTLED")

    def test_evaluate_payout_transfer_failure_keeps_retriable_state(self):
        """Payout transfer failure must retain EVALUATED_PASSED state and remain retriable."""
        jury = AgentJury()
        jury.create_bounty("Task FailPayout", "Spec FailPayout")
        MockMessage.sender_address = "0xWorkerAgent"
        jury.submit_deliverable(1, "https://github.com/test/pr/1", "Done")

        # Simulate transfer failure
        MockEVMState.should_fail_transfer = True

        with self.assertRaises(Exception) as ctx:
            jury.evaluate_and_settle(1)
        self.assertIn("remains retriable", str(ctx.exception))

        bounty = json.loads(jury.get_bounty(1))
        self.assertEqual(bounty["status"], "EVALUATED_PASSED")
        self.assertEqual(bounty["score"], 95)

        # Now simulate network recovery and retry payout
        MockEVMState.should_fail_transfer = False
        retry_res = jury.retry_payout(1)
        self.assertTrue(retry_res)

        bounty_after = json.loads(jury.get_bounty(1))
        self.assertEqual(bounty_after["status"], "SETTLED")

    def test_evaluate_and_settle_strict_fail(self):
        """Deliverable HTTP failure rejects bounty and sets status to REJECTED."""
        jury = AgentJury()
        jury.create_bounty("Task 404", "Spec 404")
        MockMessage.sender_address = "0xWorkerAgent"
        jury.submit_deliverable(1, "https://invalid-url-404.com", "Summary")

        verdict = jury.evaluate_and_settle(1)
        self.assertFalse(verdict["passed"])
        self.assertEqual(verdict["score"], 0)

        bounty = json.loads(jury.get_bounty(1))
        self.assertEqual(bounty["status"], "REJECTED")

    def test_refund_bounty_success(self):
        """Bounty creator can reclaim escrow on rejected or open bounties."""
        jury = AgentJury()
        MockMessage.sender_address = "0xAgentAlpha_Creator"
        jury.create_bounty("Task Refund", "Spec Refund")

        success = jury.refund_bounty(1)
        self.assertTrue(success)

        bounty = json.loads(jury.get_bounty(1))
        self.assertEqual(bounty["status"], "REFUNDED")

    def test_refund_transfer_failure_keeps_retriable_state(self):
        """Refund transfer failure retains REFUND_PENDING state and allows retry."""
        jury = AgentJury()
        MockMessage.sender_address = "0xAgentAlpha_Creator"
        jury.create_bounty("Task RefundFail", "Spec RefundFail")

        # Simulate transfer failure on refund
        MockEVMState.should_fail_transfer = True

        with self.assertRaises(Exception) as ctx:
            jury.refund_bounty(1)
        self.assertIn("remains retriable", str(ctx.exception))

        bounty = json.loads(jury.get_bounty(1))
        self.assertEqual(bounty["status"], "REFUND_PENDING")

        # Simulate network recovery and retry refund
        MockEVMState.should_fail_transfer = False
        retry_success = jury.refund_bounty(1)
        self.assertTrue(retry_success)

        bounty_after = json.loads(jury.get_bounty(1))
        self.assertEqual(bounty_after["status"], "REFUNDED")

    def test_refund_unauthorized_rejection(self):
        """Non-creator accounts cannot claim refund."""
        jury = AgentJury()
        MockMessage.sender_address = "0xAgentAlpha_Creator"
        jury.create_bounty("Task Auth", "Spec Auth")

        MockMessage.sender_address = "0xAttacker"
        with self.assertRaises(Exception) as ctx:
            jury.refund_bounty(1)
        self.assertIn("Only the bounty creator", str(ctx.exception))

if __name__ == '__main__':
    unittest.main()
