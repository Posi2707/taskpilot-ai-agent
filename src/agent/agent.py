"""OpenAI-compatible function-calling loop with bounded steps and trace evidence."""
import json
from typing import Any
from .tools import ToolRegistry, ToolError
from .tracing import TraceRecorder

SYSTEM_PROMPT = """You are TaskPilot, a careful task-planning assistant.
Break requests into a short ordered plan before using tools. Use tools only when needed.
Never claim a tool action succeeded unless its result confirms success. If a write tool
returns approval_required, stop and ask the user for approval; do not retry or bypass it.
Use saved memory when relevant. Do not invent task IDs or saved facts. Summarize outcomes
and mention incomplete steps honestly. Keep plans proportional to the request."""


class TaskAgent:
    def __init__(self, client: Any, model: str, tools: ToolRegistry,
                 trace: TraceRecorder | None = None, max_steps: int = 6):
        self.client = client
        self.model = model
        self.tools = tools
        self.trace = trace or TraceRecorder()
        self.max_steps = max_steps

    def run(self, user_request: str) -> str:
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_request},
        ]
        self.trace.record("run_started", request=user_request, max_steps=self.max_steps)
        for step in range(1, self.max_steps + 1):
            response = self.client.chat.completions.create(
                model=self.model, messages=messages, tools=self.tools.definitions(),
                tool_choice="auto", temperature=0.2,
            )
            message = response.choices[0].message
            if not message.tool_calls:
                answer = message.content or "I could not produce a response."
                self.trace.record("run_completed", step=step, answer=answer)
                return answer
            messages.append({"role": "assistant", "content": message.content,
                             "tool_calls": [tc.model_dump(exclude_none=True) for tc in message.tool_calls]})
            for call in message.tool_calls:
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments or "{}")
                    self.trace.record("tool_call", step=step, tool=name, arguments=args)
                    result = self.tools.execute(name, args)
                    self.trace.record("tool_result", step=step, tool=name, result=result)
                except (json.JSONDecodeError, ToolError, TypeError) as exc:
                    result = {"error": str(exc)}
                    self.trace.record("tool_error", step=step, tool=name, error=str(exc))
                messages.append({"role": "tool", "tool_call_id": call.id,
                                 "content": json.dumps(result, ensure_ascii=False)})
        self.trace.record("step_limit_reached", max_steps=self.max_steps)
        return ("I reached the maximum number of tool steps. I stopped safely; "
                "please narrow the request or split it into smaller steps.")
