import argparse
import os
from dotenv import load_dotenv
from openai import OpenAI
from .agent import TaskAgent
from .memory import MemoryStore
from .tools import ToolRegistry
from .tracing import TraceRecorder


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="TaskPilot: a tool-using task agent")
    parser.add_argument("request", nargs="?", help="What should the agent help you do?")
    parser.add_argument("--approve-writes", action="store_true",
                        help="Allow task creation/completion during this run")
    args = parser.parse_args()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY in .env first. See .env.example.")
    request = args.request or input("What would you like TaskPilot to do? ")
    memory = MemoryStore()
    approval = (lambda action: print(f"\nApproval requested: {action}") or
                input("Type YES to approve: ").strip() == "YES") if not args.approve_writes else (lambda _: True)
    registry = ToolRegistry(memory, approval=approval)
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    agent = TaskAgent(client, os.getenv("OPENAI_MODEL", "gpt-4o-mini"), registry,
                      TraceRecorder())
    print("\n" + agent.run(request))


if __name__ == "__main__":
    main()
