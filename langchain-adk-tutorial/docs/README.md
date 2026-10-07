# Documentation

Reference documentation for the LangChain and LangGraph tutorial. The tutorial itself lives next to the
code: the [README](../README.md) lists the agents and learning tracks, and each `agentNN_*/CASES.md` is one
lesson. The pages here explain how this folder is put together and how to operate it.

| Page | Read it when you want to |
|---|---|
| [Getting started](getting-started.md) | Install the project and run your first agent, on Gemini or on a local model |
| [Architecture](architecture.md) | Understand the layout, how the chat runner finds an agent, and what the shared `common/` code does |
| [Configuration](configuration.md) | Look up an environment variable, a command-line option, or `langgraph.json` |
| [Shared code reference](common-api.md) | Call `get_model`, `ask`, `embed_texts` or the RAG helpers, or reuse the chat and eval runners |
| [Agent catalog](agent-catalog.md) | See every folder's files, start command and how its `agent` is built |
| [Evals and tests](evals-and-testing.md) | Run `uv run evals` and the unit tests, and write an eval set |
| [Troubleshooting](troubleshooting.md) | Fix a setup error |
| [Contributing](../CONTRIBUTING.md) | Port the next agent, fix a lesson, or send a pull request |

## Status

Agents 01 to 14 are ported from the [Google ADK tutorial](../../google-adk-tutorial/README.md). Agents 15 to
50 and the study guide are still to come. Until then, use the ADK tutorial's
[questions.md](../../google-adk-tutorial/questions.md) for the theory: the ideas are the same, and the
[concept map](../README.md#from-adk-to-langchain) in the README translates the names.

## Where things are

| You are looking for | It is in |
|---|---|
| The lesson for one agent | `agentNN_*/CASES.md` |
| The code for one agent | `agentNN_*/agent.py` |
| The model switch | `common/models.py` |
| The terminal chat and the eval runner | `common/chat.py`, `common/evals.py` |
| The list of agents LangGraph Studio serves | `langgraph.json` |
| Settings you need to fill in | `.env.example` |
