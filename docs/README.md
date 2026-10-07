# Documentation

Reference documentation for the Google ADK tutorial. The tutorial itself lives next to the code:
the [README](../README.md) lists the agents and learning tracks, each `agentNN_*/CASES.md` is one lesson,
and [questions.md](../questions.md) is the study guide. The pages here explain how the repository is put
together and how to operate it.

| Page | Read it when you want to |
|---|---|
| [Getting started](getting-started.md) | Install the project and run your first agent, on Gemini or on a local model |
| [Architecture](architecture.md) | Understand the folder layout, how ADK finds an agent, and what the shared `common/` code does |
| [Configuration](configuration.md) | Look up an environment variable, a per-agent switch, or a port number |
| [Shared code reference](common-api.md) | Call `get_model`, `ask`, `embed_texts` or the RAG helpers from your own agent or lab |
| [Agent catalog](agent-catalog.md) | See every folder's files and start command, and which ones need a second terminal |
| [Evals and tests](evals-and-testing.md) | Run `adk eval`, the unit tests, or the measuring scripts that ship with the agents |
| [Troubleshooting](troubleshooting.md) | Fix a setup error |
| [Contributing](../CONTRIBUTING.md) | Add an agent, fix a lesson, or send a pull request |

## Where things are

| You are looking for | It is in |
|---|---|
| The lesson for one agent | `agentNN_*/CASES.md` |
| The code for one agent | `agentNN_*/agent.py` (labs have a script instead, see the [catalog](agent-catalog.md)) |
| Theory, diagrams, measured results, 100 questions | [questions.md](../questions.md) |
| The model switch | `common/models.py` |
| The sample document every RAG step searches | `data/handbook.md` |
| Settings you need to fill in | `.env.example` |
