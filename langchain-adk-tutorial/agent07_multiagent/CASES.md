# agent07_multiagent: cases, easiest first

Run: `uv run chat agent07_multiagent`, or `uv run langgraph dev` to see the hand-offs in the browser.
Concepts: several agents with narrow jobs, hand-offs between them, and the global model switch (`common/models.py`).
Topic: a travel helper with a weather specialist and a currency specialist.

## How it executes
Control: THE LLM DECIDES. The coordinator chooses a specialist from the hand-off tools' descriptions, and
the path is different for different questions.

```
 user message
      │
      ▼   enters at the ACTIVE agent (root_agent at the start)
 ┌────────────┐  general question   ┌───────────────────┐
 │ root_agent ├────────────────────►│ answers itself    │
 │ (LLM picks)│                     └───────────────────┘
 └──┬───────┬─┘
    │       │ transfer_to_currency_agent
    │       └──────────────► currency_agent ──► convert_currency() ──► answer
    │ transfer_to_weather_agent
    └──────────────────────► weather_agent  ──► get_weather() ───────► answer

 After a hand-off, the specialist keeps the next turns until control moves again.
```

How it is built: each agent is a node of a small LangGraph graph (`team` in `agent.py`). A hand-off is a tool that writes
the next agent's name into the state (`active_agent`). After an agent stops, the graph looks at that name and runs the
named agent, or ends the turn. LangChain has no ready-made "sub-agents" switch; the pattern is these few lines.

## Part A: the model switch (the global feature)

Agents from 07 onwards get their model from `common/models.get_model()`, not from hardcoded values.
Choose the provider for all of them with an environment variable:

    MODEL_PROVIDER=local  uv run chat agent07_multiagent    # LM Studio
    MODEL_PROVIDER=gemini uv run chat agent07_multiagent    # Gemini

You can also put `MODEL_PROVIDER=local` in the project root `.env` (the factory loads it).
Override a single agent: `AGENT07_MODEL_PROVIDER=gemini` beats `MODEL_PROVIDER`.
Other settings: `LOCAL_MODEL_ID`, `LOCAL_API_BASE`, `GEMINI_MODEL`.
Gemini needs the GOOGLE_* variables in the root `.env`; local needs LM Studio running.

Run case 1 under both providers and compare the answer style and speed.

## Case 1: hand-off to one specialist
> What is the weather in Tokyo?

Expect: `[transfer] root_agent -> weather_agent`, then `get_weather`, and `[weather_agent]` reports sunny, 26°C.
Learn: the coordinator picks a specialist by reading the descriptions of the hand-off tools.

## Case 2: a different specialist
> How much is 100 USD in EUR?

Expect: a hand-off to currency_agent, answer 90 EUR.
Learn: each specialist owns one narrow job and one tool.

## Case 3: no specialist needed
In a new conversation (`/new`):
> What is a passport?

Expect: `[root_agent]` answers itself, with no hand-off.
Learn: a hand-off is a choice, driven by the coordinator's instruction.

## Case 4: the specialist keeps the conversation
In one conversation, ask the weather question, then the currency question, then:
> What is a passport?

Expect: the answer comes from `[currency_agent]` (the last specialist), not root_agent. `/state` shows `"active_agent": "currency_agent"`.
Learn: after a hand-off, the specialist stays in charge of later turns until
something hands control on again. Watch the name in front of each reply.

## Case 5: a tool that fails
> What is the weather in Atlantis?

Expect: weather_agent reports "No weather data for Atlantis" and does not invent a forecast.
Learn: a tool's error message is passed through to the answer, so return clear errors.

## Case 6: two requests in one message
> What is the weather in Paris, and how much is 50 USD in SEK?

Expect: results vary by model. On `qwen3.5-9b` in testing, the coordinator called both hand-off tools at once, currency_agent
converted the money and handed on, and weather_agent gave the weather (and repeated the conversion). Another model may
answer only one part.
Learn: a hand-off gives the turn to one agent at a time, so multi-part requests are
handled by chained hand-offs, which is not guaranteed to be tidy or complete. A more
controlled way to combine specialists is a good topic for the next agent.

## Case 7: what the next agent is shown
Read `hide_handoffs` in `agent.py`.
Learn: the hand-off calls are stored in the conversation, but they are removed from what is SENT to each model. The first
version of this port did not do that, and the local model, seeing "transfer_to_weather_agent ... Transferred" in the history,
answered "I have transferred your request to the weather agent" instead of calling `get_weather`. What an agent is shown of
other agents' work is a design decision, and small models are sensitive to it.
