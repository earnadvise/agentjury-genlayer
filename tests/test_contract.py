"""
Automated Unit Tests for AgentJury GenVM Contract
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
        if "FAIL_TEST" in prompt:
            return json.dumps({
                "passed": False,
                "score": 20,
                "reasoning": "Deliverable failed criteria."
            })
        return json.dumps({
            "passed": True,
            "score": 95,
            "reasoning": "Criteria fully satisfied."
        })

    class web:
        @staticmethod
        def get(url: str) -> str:
            if "404" in url:
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
    def test_create_bounty(self):
        jury = AgentJury()
        bounty_id = jury.create_bounty("Task A", "Spec A", 100)
        self.assertEqual(bounty_id, 1)
        raw_bounty = jury.get_bounty(1)
        bounty = json.loads(raw_bounty)
        self.assertEqual(bounty["title"], "Task A")
        self.assertEqual(bounty["status"], "OPEN")

    def test_submit_deliverable(self):
        jury = AgentJury()
        jury.create_bounty("Task B", "Spec B", 250)
        MockMessage.sender_address = "0xWorkerAgent"
        success = jury.submit_deliverable(1, "https://github.com/test/pr/1", "Done")
        self.assertTrue(success)
        raw_bounty = jury.get_bounty(1)
        bounty = json.loads(raw_bounty)
        self.assertEqual(bounty["status"], "SUBMITTED")
        self.assertEqual(bounty["worker"], "0xWorkerAgent")

    def test_evaluate_and_settle_success(self):
        jury = AgentJury()
        jury.create_bounty("Task C", "Spec C", 500)
        jury.submit_deliverable(1, "https://github.com/test/pr/1", "Done")
        verdict = jury.evaluate_and_settle(1)
        self.assertTrue(verdict["passed"])
        self.assertEqual(verdict["score"], 95)
        raw_bounty = jury.get_bounty(1)
        bounty = json.loads(raw_bounty)
        self.assertEqual(bounty["status"], "SETTLED")

    def test_evaluate_and_settle_strict_fail(self):
        jury = AgentJury()
        jury.create_bounty("Task D", "Spec D", 500)
        jury.submit_deliverable(1, "https://invalid-url-404.com", "Summary")
        verdict = jury.evaluate_and_settle(1)
        self.assertFalse(verdict["passed"])
        self.assertEqual(verdict["score"], 0)
        raw_bounty = jury.get_bounty(1)
        bounty = json.loads(raw_bounty)
        self.assertEqual(bounty["status"], "REJECTED")

    def test_refund_bounty(self):
        jury = AgentJury()
        MockMessage.sender_address = "0xAgentAlpha_Creator"
        jury.create_bounty("Task E", "Spec E", 300)
        success = jury.refund_bounty(1)
        self.assertTrue(success)
        raw_bounty = jury.get_bounty(1)
        bounty = json.loads(raw_bounty)
        self.assertEqual(bounty["status"], "REFUNDED")

if __name__ == '__main__':
    unittest.main()
