# Agentic AI, step by step

Two hands-on tutorials that teach the same ideas with two different frameworks. Each one is a series of
small agents: every `agentNN_*` folder adds exactly one new idea to the one before it, and has a `CASES.md`
with a diagram of how it executes plus small cases to try, easiest first.

| Folder | Framework | Status |
|---|---|---|
| [`google-adk-tutorial`](google-adk-tutorial/README.md) | [Google ADK](https://google.github.io/adk-docs/) | Complete: 50 agents, a capstone, a study guide with 100 questions, and [reference documentation](google-adk-tutorial/docs/README.md) |
| [`langchain-adk-tutorial`](langchain-adk-tutorial/README.md) | [LangChain](https://docs.langchain.com/) and LangGraph | In progress: agents 01 to 14 are ported, with [reference documentation](langchain-adk-tutorial/docs/README.md) |

The LangChain tutorial is a port of the Google ADK one: the same agents, the same topics and the same
cases. Its README has a table that maps each ADK concept to its LangChain equivalent, so you can read the
two side by side.

## Which one to start with

- **New to agents:** start with [`google-adk-tutorial`](google-adk-tutorial/README.md). It is complete and
  comes with the study guide.
- **Already using LangChain or LangGraph:** start with
  [`langchain-adk-tutorial`](langchain-adk-tutorial/README.md) and use the ADK tutorial for the topics that
  are not ported yet.

## Quick start

Each folder is its own Python project with its own dependencies and its own `.env`. Both use
[uv](https://docs.astral.sh/uv/) and run on Gemini (Google Cloud) or on a local model in
[LM Studio](https://lmstudio.ai/).

    git clone https://github.com/sagaryeole/AgenticDemo.git
    cd AgenticDemo/google-adk-tutorial        # or langchain-adk-tutorial
    uv sync
    cp .env.example .env

Then follow the Setup section of that folder's README.

| | Google ADK | LangChain |
|---|---|---|
| Chat in the terminal | `uv run adk run agent07_multiagent` | `uv run chat agent07_multiagent` |
| Browser UI | `uv run adk web` | `uv run langgraph dev` |
| Run the evals | `uv run adk eval ...` | `uv run evals ...` |
| Unit tests, no model needed | `uv run pytest` | `uv run pytest` |

## Contributing

Fixes and new lessons are welcome. Each tutorial has its own guide:
[google-adk-tutorial/CONTRIBUTING.md](google-adk-tutorial/CONTRIBUTING.md) and
[langchain-adk-tutorial/CONTRIBUTING.md](langchain-adk-tutorial/CONTRIBUTING.md), which explains how to port the
next agent.

## License

[Apache License 2.0](LICENSE).
