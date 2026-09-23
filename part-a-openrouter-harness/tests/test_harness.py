from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

PART_A = Path(__file__).parents[1]
sys.path.insert(0, str(PART_A))

from harness.agent import Agent
from harness.client import ScriptedDemoClient
from harness.tools import ToolError, WorkspaceTools


class WorkspaceToolsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temp.name)
        self.tools = WorkspaceTools(self.workspace)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_write_then_read(self) -> None:
        result = self.tools.execute("write_file", {"path": "src/demo.txt", "content": "hello"})
        self.assertEqual(result["bytes"], 5)
        read = self.tools.execute("read_file", {"path": "src/demo.txt"})
        self.assertEqual(read["content"], "hello")

    def test_path_traversal_is_rejected(self) -> None:
        with self.assertRaises(ToolError):
            self.tools.execute("read_file", {"path": "../secret.txt"})

    def test_non_allowlisted_command_is_rejected(self) -> None:
        with self.assertRaises(ToolError):
            self.tools.execute("run_command", {"program": "powershell", "arguments": ["pwd"]})


class AgentLoopTests(unittest.TestCase):
    def test_scripted_model_exercises_complete_loop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            agent = Agent(ScriptedDemoClient(), WorkspaceTools(workspace), max_steps=6)
            result = agent.run("Create and execute hello.py")
            self.assertEqual(result.steps, 4)
            self.assertTrue((workspace / "hello.py").is_file())
            tool_messages = [message for message in result.messages if message["role"] == "tool"]
            self.assertEqual(len(tool_messages), 3)
            self.assertEqual(len({message["tool_call_id"] for message in tool_messages}), 3)
            command_result = json.loads(tool_messages[-1]["content"])
            self.assertEqual(command_result["value"]["exit_code"], 0)


if __name__ == "__main__":
    unittest.main()
