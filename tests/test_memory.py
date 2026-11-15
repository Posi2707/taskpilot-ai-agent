from agent.memory import MemoryStore


def test_task_lifecycle_and_priority_order():
    memory = MemoryStore(":memory:")
    low = memory.add_task("Update portfolio", "low")
    high = memory.add_task("Prepare agent demo", "high")
    assert [t["id"] for t in memory.list_tasks("open")] == [high["id"], low["id"]]
    done = memory.complete_task(high["id"])
    assert done["status"] == "done"
    assert len(memory.list_tasks("open")) == 1
    assert len(memory.list_tasks("done")) == 1


def test_memory_search():
    memory = MemoryStore(":memory:")
    memory.add_task("Build Python agent", "high")
    memory.add_note("The agent should write JSONL traces")
    assert len(memory.search_memory("agent")) == 2
