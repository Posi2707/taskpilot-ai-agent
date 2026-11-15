"""Validated tools exposed to the model. Writes are approval-gated."""
from typing import Any, Callable
from pydantic import ValidationError
from .memory import MemoryStore
from .schemas import AddTaskArgs, ListTasksArgs, CompleteTaskArgs, SearchMemoryArgs


class ToolError(Exception):
    pass


class ToolRegistry:
    def __init__(self, memory: MemoryStore, approval: Callable[[str], bool] | None = None):
        self.memory = memory
        self.approval = approval or (lambda _description: False)
        self._handlers = {
            "list_tasks": (ListTasksArgs, self._list_tasks, False),
            "add_task": (AddTaskArgs, self._add_task, True),
            "complete_task": (CompleteTaskArgs, self._complete_task, True),
            "search_memory": (SearchMemoryArgs, self._search_memory, False),
        }

    def definitions(self) -> list[dict[str, Any]]:
        descriptions = {
            "list_tasks": "List saved tasks, optionally filtered by open or done status.",
            "add_task": "Create a task. Requires user approval before writing to memory.",
            "complete_task": "Mark a task complete by ID. Requires user approval.",
            "search_memory": "Search saved task titles and notes for a keyword.",
        }
        return [{"type": "function", "function": {
            "name": name, "description": descriptions[name],
            "parameters": schema.model_json_schema(),
        }} for name, (schema, _, _) in self._handlers.items()]

    def execute(self, name: str, raw_args: dict[str, Any]) -> dict[str, Any]:
        if name not in self._handlers:
            raise ToolError(f"Unknown tool: {name}")
        schema, handler, is_write = self._handlers[name]
        try:
            args = schema.model_validate(raw_args)
        except ValidationError as exc:
            raise ToolError(f"Invalid arguments: {exc.errors(include_url=False)}") from exc
        if is_write:
            summary = f"{name}({args.model_dump()})"
            if not self.approval(summary):
                return {"status": "approval_required", "action": summary,
                        "message": "No change was made. Ask the user for explicit approval."}
        return handler(args)

    def _list_tasks(self, args: ListTasksArgs) -> dict[str, Any]:
        return {"tasks": self.memory.list_tasks(args.status)}

    def _add_task(self, args: AddTaskArgs) -> dict[str, Any]:
        return {"task": self.memory.add_task(args.title, args.priority)}

    def _complete_task(self, args: CompleteTaskArgs) -> dict[str, Any]:
        task = self.memory.complete_task(args.task_id)
        if not task:
            return {"error": "Task not found", "task_id": args.task_id}
        return {"task": task}

    def _search_memory(self, args: SearchMemoryArgs) -> dict[str, Any]:
        return {"matches": self.memory.search_memory(args.query)}
