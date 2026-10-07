"""Chat with any agent of this tutorial in the terminal.

    uv run chat agent07_multiagent
    uv run chat agent48_permissions --user Alma --set role=student --set user_name=Alma

It imports `<folder>/agent.py`, takes the object called `agent` (or awaits `make_agent()` when the agent needs
async set-up, as in agent12), and then loops: read a line, run the agent, print what happened.

What it adds around the agent, because a LangChain agent is only a graph and keeps nothing by itself:
  a CHECKPOINTER  remembers the conversation (the "thread") between your lines. Here it lives in memory, so it is
                  lost when you quit. agent34 swaps in a database.
  a STORE         data that outlives one conversation (agent21, agent34). Also in memory here.
  a CONTEXT       facts about the caller that the application decides (who is logged in), built from --user / --set.

Commands while chatting:  /new  start a new conversation     /state  show this conversation's state     exit  quit
"""
import argparse
import asyncio
import dataclasses
import importlib
import inspect
import json
import logging
import sys
import uuid
from pathlib import Path

from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

YES = {"y", "yes"}


# The in-memory checkpointer logs a warning the first time it reads back one of the tutorial's own classes from the state
# (such as agent06's ReviewAnalysis). That is expected here, so only real errors from that logger are shown.
logging.getLogger("langgraph.checkpoint.serde.jsonplus").setLevel(logging.ERROR)


async def load_agent(folder: str, attribute: str = "agent"):
    """Import <folder>.agent and return its agent. `make_agent()` (sync or async) wins over a plain `agent` object."""
    sys.path.insert(0, str(Path.cwd()))
    module = importlib.import_module(f"{folder.rstrip('/').replace('/', '.')}.agent")
    if hasattr(module, "make_agent"):
        made = module.make_agent()
        return await made if inspect.isawaitable(made) else made
    return getattr(module, attribute)


def build_context(agent, user: str, settings: dict):
    """Fill the agent's context_schema (a dataclass) from --user and --set. Agents without one get no context."""
    schema = getattr(agent, "context_schema", None)
    if schema is None or not dataclasses.is_dataclass(schema):
        return None
    names = {f.name for f in dataclasses.fields(schema)}
    values = {k: v for k, v in settings.items() if k in names}
    if "user_id" in names:
        values.setdefault("user_id", user)
    return schema(**values)


def short(value, limit: int = 300) -> str:
    if isinstance(value, list) and value and all(isinstance(b, dict) and b.get("type") == "text" for b in value):
        value = " ".join(" ".join(b["text"].split()) for b in value)   # MCP tools return a list of text blocks (agent12)
    text = value if isinstance(value, str) else json.dumps(value, default=str)
    return text if len(text) <= limit else text[:limit] + "..."


async def ask_human(interrupt_value) -> object:
    """An agent paused and is waiting for a person. Ask on the terminal and return the answer to resume with."""
    if isinstance(interrupt_value, dict) and "action_requests" in interrupt_value:   # HumanInTheLoopMiddleware (agent15)
        decisions = []
        for action in interrupt_value["action_requests"]:
            print(f"[approval needed] {action['name']}({action['args']})")
            answer = (await asyncio.to_thread(input, "approve? (yes/no): ")).strip().lower()
            decisions.append({"type": "approve"} if answer in YES else {"type": "reject"})
        return {"decisions": decisions}
    print(f"[paused for input] {short(interrupt_value)}")   # a tool that called interrupt() itself (agent33)
    return (await asyncio.to_thread(input, "answer: ")).strip()


async def run_turn(agent, payload, config: dict, context, show_tokens: bool = False, shown: set | None = None) -> None:
    """Run the agent on one user line. Tool calls are printed as they happen. Replies are printed when the turn ends or
    pauses (or word by word with --stream): a guardrail may still replace a reply after the model wrote it (agent11),
    and only the final version should be shown."""
    while True:
        interrupt_value, streamed = None, False
        replies: dict[str, AIMessage] = {}   # message id -> latest version of that reply, in the order they first appeared
        shown = set() if shown is None else shown   # (message id, text) already printed: a sub-agent reports its whole history again
        async for mode, chunk in agent.astream(payload, config, context=context, stream_mode=["updates", "messages"]):
            if mode == "messages":
                message, _ = chunk
                if show_tokens and isinstance(message, AIMessageChunk) and message.text:
                    print(message.text, end="", flush=True)
                    streamed = True
                continue
            for node, update in chunk.items():
                if node == "__interrupt__":
                    interrupt_value = update[0].value
                    continue
                for message in (update or {}).get("messages", []) if isinstance(update, dict) else []:
                    key = message.tool_call_id if isinstance(message, ToolMessage) else (message.id, message.text)
                    if key in shown:
                        continue
                    shown.add(key)
                    if isinstance(message, AIMessage):
                        for call in message.tool_calls:
                            print(f"[tool call] {call['name']}({short(call['args'])})")
                        searches = (message.response_metadata.get("grounding_metadata") or {}).get("web_search_queries")
                        if searches:   # Gemini's built-in search runs on Google's side, so it is not a tool call here (agent02)
                            print(f"[google_search] {searches}")
                        if message.text.strip():
                            replies[message.id] = message
                    elif isinstance(message, ToolMessage):
                        print(f"[tool result] {message.name}: {short(message.content)}")
        if streamed:
            print()
        else:
            for message in replies.values():
                print(f"[{message.name or 'agent'}]: {message.text}")
        if interrupt_value is None:
            break
        payload = Command(resume=await ask_human(interrupt_value))   # carry on from the pause, in the same thread

    values = (await agent.aget_state(config)).values
    structured = values.get("structured_response")
    if structured is not None and not replies:   # an agent with response_format: the result is an object, not text (agent06)
        as_json = structured.model_dump_json(indent=2) if hasattr(structured, "model_dump_json") else json.dumps(structured, indent=2)
        print(f"[structured]: {as_json}")


async def chat(args) -> None:
    agent = await load_agent(args.agent)
    if agent.checkpointer is None:
        agent.checkpointer = InMemorySaver()
    if agent.store is None:
        agent.store = InMemoryStore()
    settings = dict(pair.split("=", 1) for pair in args.set)
    context = build_context(agent, args.user, settings)
    thread, shown = str(uuid.uuid4()), set()
    print(f"Chatting with {args.agent}. Type exit to quit, /new for a new conversation, /state to see the state.")
    while True:
        try:
            line = (await asyncio.to_thread(input, "[user]: ")).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        if line.lower() in ("exit", "quit"):
            break
        config = {"configurable": {"thread_id": thread}, "metadata": {"user_id": args.user}}
        if line == "/new":
            thread = str(uuid.uuid4())
            print("(new conversation)")
            continue
        if line == "/state":
            values = (await agent.aget_state(config)).values
            print(short({k: v for k, v in values.items() if k != "messages"} | {"messages": len(values.get("messages", []))}, 2000))
            continue
        await run_turn(agent, {"messages": [{"role": "user", "content": line}]}, config, context, args.stream, shown)


def main() -> None:
    parser = argparse.ArgumentParser(description="Chat with an agent of this tutorial in the terminal.")
    parser.add_argument("agent", help="the agent folder, e.g. agent07_multiagent")
    parser.add_argument("--user", default="student", help="who is chatting (the user id)")
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                        help="a value for the agent's context, e.g. --set role=teacher (repeat for more)")
    parser.add_argument("--stream", action="store_true", help="print the reply while it is being written")
    asyncio.run(chat(parser.parse_args()))


if __name__ == "__main__":
    main()
