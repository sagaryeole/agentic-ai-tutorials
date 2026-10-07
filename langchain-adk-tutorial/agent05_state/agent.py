import json

from langchain.agents import AgentState, create_agent
from langchain.tools import ToolRuntime
from langchain_core.messages import ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.types import Command

# LM Studio's OpenAI-compatible server (Developer tab -> Start Server)
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"


# State: a dict that LangGraph stores with the conversation (the "thread"). An agent's state always has
# `messages`; this class adds one more key. It survives across turns in the same thread, and is empty in a new one.
class NotesState(AgentState):
    notes: list[str]


# A tool reads state through `runtime` (LangChain fills it in; the model never sees this parameter).
# A tool WRITES state by returning a Command: "update these keys". Changing runtime.state in place is not saved.
def save_note(note: str, runtime: ToolRuntime) -> Command:
    """Saves a note so it can be recalled later in this conversation.

    Args:
        note: The text to remember, e.g. "dentist appointment on Friday at 14:00".
    """
    notes = list(runtime.state.get("notes", []))
    notes.append(note)
    result = {"status": "saved", "total_notes": len(notes)}
    return Command(update={
        "notes": notes,
        # A Command replaces the normal return value, so the tool result for the model is added by hand.
        "messages": [ToolMessage(json.dumps(result), tool_call_id=runtime.tool_call_id)],
    })


def list_notes(runtime: ToolRuntime) -> dict:
    """Returns every note saved so far in this conversation."""
    return {"notes": runtime.state.get("notes", [])}


agent = create_agent(
    model=ChatOpenAI(
        model="qwen3.5-9b",
        base_url=LM_STUDIO_URL,
        api_key="lm-studio",
    ),
    name="root_agent",
    system_prompt=(
        "You keep notes for the user. When they ask you to remember or note "
        "something, call save_note. When they ask what you have noted or "
        "remembered, call list_notes and answer only from its output. "
        "Never invent notes."
    ),
    tools=[save_note, list_notes],
    state_schema=NotesState,
)
