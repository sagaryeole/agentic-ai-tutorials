# Agentic AI with LangChain and LangGraph, step by step

A hands-on tutorial. Each `agentNN_*` folder adds exactly one new idea to the one before it, and has a
`CASES.md` with a diagram of how it executes plus small cases to try, easiest first.

This is the LangChain port of the Google ADK tutorial in `../google-adk-tutorial`: the same agents, the same
topics and the same cases, built with `langchain` (`create_agent`, middleware) and `langgraph` (graphs, state, checkpoints).
**Agents 01 to 14 are ported so far.** Agents 15 to 50 and the study guide (`questions.md`) are still to come.

## Documentation

| | |
|---|---|
| [Getting started](docs/getting-started.md) | Install, set up Gemini or a local model, run your first agent |
| [Architecture](docs/architecture.md) | The folder layout, how the chat runner finds an agent, the shared `common/` code |
| [Configuration](docs/configuration.md) | Every environment variable, command-line option and `langgraph.json` |
| [Shared code reference](docs/common-api.md) | `get_model`, the chat and eval runners, `ask`, `embed_texts` and the RAG helpers |
| [Agent catalog](docs/agent-catalog.md) | Each folder's files, start command and how its agent is built |
| [Evals and tests](docs/evals-and-testing.md) | `uv run evals`, the eval set format and the unit tests |
| [Troubleshooting](docs/troubleshooting.md) | Fixes for common setup errors |
| [Contributing](CONTRIBUTING.md) | How to port the next agent or fix a lesson |

## Learning tracks

New to LangChain? Go in order. Looking for one topic? Pick a track. Each link opens that agent's `CASES.md`.

### 🟢 Core fundamentals

Instructions, tools, local models, state and structured output.

[01](agent01_poet/CASES.md) · [02](agent02_toolcall/CASES.md) · [03](agent03_localmodel/CASES.md) · [04](agent04_localmodelwithtool/CASES.md) · [05](agent05_state/CASES.md) · [06](agent06_structured/CASES.md)

### 🟡 Orchestration & workflows

Several agents working together: coordinators, pipelines, parallel steps, loops and agents as tools.

[07](agent07_multiagent/CASES.md) · [08](agent08_workflow/CASES.md) · [09](agent09_parallel/CASES.md) · [10](agent10_loop/CASES.md) · [14](agent14_agent_as_tool/CASES.md)

### 🔴 Tools, evals, safety & production

Guardrails, MCP tools and evals.

[11](agent11_guardrails/CASES.md) · [12](agent12_mcp/CASES.md) · [13](agent13_evals/CASES.md)

## The agents

| # | Folder | New idea | Model |
|---|---|---|---|
| 01 | `agent01_poet` | Instruction (`system_prompt`) | Gemini |
| 02 | `agent02_toolcall` | Built-in tool (`google_search`) | Gemini |
| 03 | `agent03_localmodel` | Local model through `ChatOpenAI` + LM Studio | local |
| 04 | `agent04_localmodelwithtool` | Your own Python function as a tool | local |
| 05 | `agent05_state` | State shared across turns (`state_schema`, `Command`) | local |
| 06 | `agent06_structured` | Structured output (`response_format`) | local |
| 07 | `agent07_multiagent` | Coordinator + specialists with hand-offs (LLM decides) and the global model switch | switchable |
| 08 | `agent08_workflow` | `StateGraph`: a fixed pipeline of nodes and edges | switchable |
| 09 | `agent09_parallel` | Parallel nodes: fan out, then fan in | switchable |
| 10 | `agent10_loop` | A conditional edge: repeat until good, with a safety cap | switchable |
| 11 | `agent11_guardrails` | Middleware: block input, validate tool args, edit output | switchable |
| 12 | `agent12_mcp` | Tools from a separate MCP server | switchable |
| 13 | `agent13_evals` | Automated evals with `uv run evals` | switchable |
| 14 | `agent14_agent_as_tool` | An agent used as a tool, and typed input | switchable |

Notes on this table:
- "switchable" means the model comes from `MODEL_PROVIDER` (see Setup).
- `common/` holds the shared code: `models.py` (the model switch), `chat.py` (the terminal chat), `evals.py` (the eval runner),
  and `llm.py`, `embeddings.py`, `rag.py` (already ported for the later RAG steps; `tests/test_rag.py` covers `rag.py`).

## From ADK to LangChain

| Google ADK | Here |
|---|---|
| `Agent(model, instruction, tools)` | `create_agent(model, system_prompt=..., tools=...)` |
| `adk run <agent>` | `uv run chat <agent>` (`common/chat.py`) |
| `adk web` | `uv run langgraph dev` (LangGraph Studio in the browser) |
| `adk eval` | `uv run evals` (`common/evals.py`) |
| session, session state | thread, state (kept by a *checkpointer*) |
| `tool_context.state[...] = ...` | the tool returns `Command(update={...})` |
| `output_schema`, `output_key` | `response_format`, `state["structured_response"]` |
| `sub_agents` (transfer) | hand-off tools + a small graph (agent07) |
| `SequentialAgent`, `ParallelAgent`, `LoopAgent` | one `StateGraph` with different edges (agents 08-10) |
| callbacks (`before_model_callback`, ...) | middleware (`@before_model`, `@wrap_tool_call`, `@after_model`) |
| `McpToolset` | `MultiServerMCPClient(...).get_tools()` |
| `AgentTool` | a `@tool` function that invokes the other agent |

## Setup

1. Install [uv](https://docs.astral.sh/uv/). It installs the right Python and all packages for you.
2. Install dependencies:

       uv sync

3. Create your config from the example and fill in your project id:

       cp .env.example .env

   One `.env` in the project root is enough: `common/models.py` loads it, and every agent imports that module. `.env` is git-ignored.
4. For Gemini (agents 01-02, and 07+ with `MODEL_PROVIDER=gemini`), set up Google Cloud once:

       gcloud auth login
       gcloud auth application-default login
       gcloud auth application-default set-quota-project YOUR_PROJECT_ID
       gcloud config set project YOUR_PROJECT_ID
       gcloud services enable aiplatform.googleapis.com

5. For a local model (agents 03-06, and 07+ with `MODEL_PROVIDER=local`): install
   [LM Studio](https://lmstudio.ai/), load a model, and start the server in the Developer tab.
   Set `LOCAL_MODEL_ID` in `.env` to the id shown by `curl http://127.0.0.1:1234/v1/models`.

If you see `API key required for Gemini Developer API`, the Gemini settings in `.env` are missing
(`GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`).
Gemini can answer `429 RESOURCE_EXHAUSTED` when many calls arrive quickly. Agents 07+ retry automatically (see `common/models.py`);
if it still fails, wait a minute and try again.

## Run

    uv run chat agent07_multiagent         # chat in the terminal
    uv run langgraph dev                   # a local server plus LangGraph Studio in the browser: graph, steps and state

In the terminal chat: `/new` starts a new conversation, `/state` prints the conversation's state, `exit` quits.
`uv run chat <agent> --stream` prints the reply while it is being written.
`langgraph dev` serves every agent listed in `langgraph.json`. Studio is a web page hosted by LangChain that talks to the
server on your machine; it may ask you to sign in to a free LangSmith account.

Switch the model for agents 07+ without editing code:

    MODEL_PROVIDER=local  uv run chat agent08_workflow
    MODEL_PROVIDER=gemini uv run chat agent08_workflow

Run the evals (agent 13):

    uv run evals agent13_evals agent13_evals/bookshop.evalset.json \
        --config agent13_evals/test_config.json

Run the model-free unit tests:

    uv run pytest

## How to study

1. Go through the agents in order. Each `CASES.md` starts with a diagram, then cases from easy to hard.
2. Run each case yourself, compare with the "Expect" line, then read "Learn".
3. Results that involve a language model can differ between runs and between Gemini and the local model.
   The "Expect" lines say what happened when the case was tested.

## Contributing

Fixes and newly ported agents are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache License 2.0](LICENSE).
