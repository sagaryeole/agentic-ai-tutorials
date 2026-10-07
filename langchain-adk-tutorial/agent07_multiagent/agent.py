from typing import Annotated

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import wrap_model_call
from langchain.tools import ToolRuntime, tool
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from common.models import get_model  # global model switch, see common/models.py

MODEL_KEY = "agent07"  # lets AGENT07_MODEL_PROVIDER override the global choice


def get_weather(city: str) -> dict:
    """Returns the current weather for a city.

    Args:
        city: City name, e.g. 'Paris' or 'Tokyo'.
    """
    fake = {
        "paris": {"temp_c": 18, "condition": "cloudy"},
        "tokyo": {"temp_c": 26, "condition": "sunny"},
        "stockholm": {"temp_c": 9, "condition": "rainy"},
    }
    data = fake.get(city.lower())
    if data is None:
        return {"status": "error", "message": f"No weather data for {city}"}
    return {"status": "success", "city": city, **data}


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Converts an amount between currencies using fixed demo rates.

    Args:
        amount: The amount to convert.
        from_currency: Three-letter code, e.g. 'USD'.
        to_currency: Three-letter code, e.g. 'EUR'.
    """
    per_usd = {"USD": 1.0, "EUR": 0.9, "JPY": 150.0, "SEK": 10.5}
    src, dst = from_currency.upper(), to_currency.upper()
    if src not in per_usd or dst not in per_usd:
        return {"status": "error", "message": f"Supported currencies: {', '.join(per_usd)}"}
    result = amount / per_usd[src] * per_usd[dst]
    return {"status": "success", "result": round(result, 2), "currency": dst}


# The shared state of the team: the conversation, plus the name of the agent that currently "has" it.
# (The second part of Annotated says what to do if two hand-offs happen in one step: the later one wins.)
class TeamState(AgentState):
    active_agent: Annotated[str, lambda old, new: new]


# A HAND-OFF is an ordinary tool. It computes nothing: it writes the name of the next agent into the state.
# return_direct=True makes the calling agent stop right after its tools ran, instead of asking its model again.
# The description is what the model reads when it decides who to hand a request to.
def transfer_to(agent_name: str, description: str):
    @tool(f"transfer_to_{agent_name}", description=f"Hand the conversation over to {agent_name}. {description}", return_direct=True)
    def transfer(runtime: ToolRuntime) -> Command:
        print(f"[transfer] {runtime.state['messages'][-1].name} -> {agent_name}")
        return Command(update={
            "active_agent": agent_name,
            "messages": [ToolMessage(f"Transferred to {agent_name}.", tool_call_id=runtime.tool_call_id)],
        })
    return transfer


# Hand-off calls stay in the stored conversation, but they are bookkeeping, so the MODEL is not shown them: a small model
# that reads "transfer_to_weather_agent ... Transferred" in the history tends to reply "I have transferred you" instead of
# doing the job. This runs before every model call of every agent and changes only what is sent, not what is stored.
@wrap_model_call
async def hide_handoffs(request, handler):
    visible = []
    for message in request.messages:
        if isinstance(message, ToolMessage) and (message.name or "").startswith("transfer_to_"):
            continue
        if isinstance(message, AIMessage) and any(c["name"].startswith("transfer_to_") for c in message.tool_calls):
            other_calls = [c for c in message.tool_calls if not c["name"].startswith("transfer_to_")]
            if not other_calls:
                continue
            message = AIMessage(content=message.text, tool_calls=other_calls, name=message.name, id=message.id)
        visible.append(message)
    return await handler(request.override(messages=visible))


DESCRIPTIONS = {
    "root_agent": "Travel helper for general questions; routes other questions to the right specialist.",
    "weather_agent": "Gives the current weather for a city.",
    "currency_agent": "Converts money between currencies.",
}


def transfers(me: str) -> list:
    """Hand-off tools to every other agent of the team."""
    return [transfer_to(name, description) for name, description in DESCRIPTIONS.items() if name != me]


# Specialists: each has one narrow job and one tool (plus the hand-off tools).
weather_agent = create_agent(
    name="weather_agent",
    model=get_model(MODEL_KEY),
    system_prompt=(
        "Call get_weather for the city the user names and report exactly what it returns. Never invent weather data. "
        "If part of the request is another agent's job and has not been answered yet, transfer to that agent."
    ),
    tools=[get_weather, *transfers("weather_agent")],
    state_schema=TeamState,
    middleware=[hide_handoffs],
)

currency_agent = create_agent(
    name="currency_agent",
    model=get_model(MODEL_KEY),
    system_prompt=(
        "Call convert_currency with the amount and currency codes the user gives, and report the result. Never guess a rate. "
        "If part of the request is another agent's job and has not been answered yet, transfer to that agent."
    ),
    tools=[convert_currency, *transfers("currency_agent")],
    state_schema=TeamState,
    middleware=[hide_handoffs],
)

# Coordinator: has no tools of its own, only hand-offs to the specialists.
root_agent = create_agent(
    name="root_agent",
    model=get_model(MODEL_KEY),
    system_prompt=(
        "You are a travel helper. For weather questions, transfer to weather_agent. "
        "For money or currency conversion, transfer to currency_agent. "
        "Answer anything else yourself."
    ),
    tools=transfers("root_agent"),
    state_schema=TeamState,
    middleware=[hide_handoffs],
)


def who_is_active(state: TeamState) -> str:
    """Each new user message goes to the agent that had the conversation last (the coordinator at the start)."""
    return state.get("active_agent") or "root_agent"


def after_agent(state: TeamState) -> str:
    """An agent just stopped. If its last act was a hand-off, the named agent runs next; otherwise the turn is over."""
    last = state["messages"][-1]
    handed_off = isinstance(last, ToolMessage) and (last.name or "").startswith("transfer_to_")
    return state["active_agent"] if handed_off else END


# The team is a graph with one node per agent. A turn enters at the active agent and ends when an agent gives its answer.
team = StateGraph(TeamState)
for name, member in [("root_agent", root_agent), ("weather_agent", weather_agent), ("currency_agent", currency_agent)]:
    team.add_node(name, member)
    team.add_conditional_edges(name, after_agent, [n for n in DESCRIPTIONS if n != name] + [END])
team.add_conditional_edges(START, who_is_active, list(DESCRIPTIONS))
agent = team.compile(name="travel_team")
