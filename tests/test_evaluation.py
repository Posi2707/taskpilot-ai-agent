"""Small deterministic checks for tool policy and observable outcomes."""
from agent.memory import MemoryStore
from agent.tools import ToolRegistry


def test_eval_read_tool_returns_empty_state():
    tools = ToolRegistry(MemoryStore(":memory:"))
    result = tools.execute("list_tasks", {"status": "open"})
    assert result == {"tasks": []}


def test_eval_approval_gate_does_not_mutate_state():
    memory = MemoryStore(":memory:")
    tools = ToolRegistry(memory, approval=lambda _: False)
    result = tools.execute("complete_task", {"task_id": 99})
    assert result["status"] == "approval_required"
    assert memory.list_tasks() == []
