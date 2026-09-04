"""
Automated Unit Tests for AgentJury GenVM Contract
"""

import sys
import os
import json
import unittest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Create a module mock for genlayer
import types
mock_genlayer = types.ModuleType("genlayer")

class MockGL:
    class message:
        sender = "0xAgentAlpha_Creator"

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
            if "FAIL_TEST" in prompt:
                return json.dumps({
                    "passed": False,
                    "score": 20,
                    "reasoning": "Deliverable failed unit tests and criteria."
                })
            return json.dumps({
                "passed": True,
                "score": 95,
                "reasoning": "Criteria fully satisfied."
            })

        class web:
            @staticmethod
            def get(url: str) -> str:
                return "def solution(): return True"

    class eq_principle:
        @staticmethod
        def strict_eq(func):
            return func()

    class Contract:
        pass

mock_genlayer.gl = MockGL
sys.modules['genlayer'] = mock_genlayer

from contracts.agent_jury import AgentJury

class TestAgentJury(unittest.TestCase):
    def test_create_bounty(self):
        jury = AgentJury()
        bounty_id = jury.create_bounty("Task A", "Spec A", 100)
        self.assertEqual(bounty_id, 1)
        bounty = jury.get_bounty(1)
        self.assertEqual(bounty["title"], "Task A")
        self.assertEqual(bounty["reward"], 100)
        self.assertEqual(bounty["status"], "OPEN")

    def test_submit_deliverable(self):
        jury = AgentJury()
        jury.create_bounty("Task B", "Spec B", 250)
        MockGL.message.sender = "0xWorkerAgent"
        success = jury.submit_deliverable(1, "https://github.com/test/pr/1", "Done")
        self.assertTrue(success)
        bounty = jury.get_bounty(1)
        self.assertEqual(bounty["status"], "SUBMITTED")
        self.assertEqual(bounty["worker"], "0xWorkerAgent")

    def test_evaluate_and_settle_success(self):
        jury = AgentJury()
        jury.create_bounty("Task C", "Spec C", 500)
        jury.submit_deliverable(1, "https://github.com/test/pr/1", "Done")
        verdict = jury.evaluate_and_settle(1)
        self.assertTrue(verdict["passed"])
        self.assertEqual(verdict["score"], 95)
        bounty = jury.get_bounty(1)
        self.assertEqual(bounty["status"], "SETTLED")

    def test_evaluate_and_settle_rejection(self):
        jury = AgentJury()
        jury.create_bounty("Task D", "FAIL_TEST: Spec D", 500)
        jury.submit_deliverable(1, "https://github.com/test/pr/2", "Done")
        verdict = jury.evaluate_and_settle(1)
        self.assertFalse(verdict["passed"])
        self.assertEqual(verdict["score"], 20)
        bounty = jury.get_bounty(1)
        self.assertEqual(bounty["status"], "REJECTED")

if __name__ == "__main__":
    unittest.main()
