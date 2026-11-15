from agent.memory import MemoryStore
from agent.tools import ToolRegistry, ToolError


def test_write_requires_approval():
    memory = MemoryStore(":memory:")
    tools = ToolRegistry(memory, approval=lambda _: False)
    result = tools.execute("add_task", {"title": "Prepare demo", "priority": "high"})
    assert result["status"] == "approval_required"
    assert memory.list_tasks() == []


def test_write_succeeds_after_approval():
    memory = MemoryStore(":memory:")
    tools = ToolRegistry(memory, approval=lambda _: True)
    result = tools.execute("add_task", {"title": "Prepare demo", "priority": "high"})
    assert result["task"]["title"] == "Prepare demo"


def test_schema_rejects_unexpected_arguments():
    tools = ToolRegistry(MemoryStore(":memory:"))
    try:
        tools.execute("list_tasks", {"status": "all", "drop_database": True})
    except ToolError:
        pass
    else:
        raise AssertionError("Unexpected arguments should be rejected")


def test_unknown_tool_is_rejected():
    tools = ToolRegistry(MemoryStore(":memory:"))
    try:
        tools.execute("shell", {"command": "whoami"})
    except ToolError:
        pass
    else:
        raise AssertionError("Unknown tool should be rejected")
