# Agent catalog

Every lesson folder, its start command and how its agent is built. The folder name links to the lesson.
For what each one teaches, see the table in the [README](../README.md#the-agents).

All 14 are agents you chat with: `uv run chat <folder>`, or pick the graph in `uv run langgraph dev`.

| # | Folder | Built with | Model | Other files |
|---|---|---|---|---|
| 01 | [`agent01_poet`](../agent01_poet/CASES.md) | `create_agent` | Gemini, written in `agent.py` | - |
| 02 | [`agent02_toolcall`](../agent02_toolcall/CASES.md) | `create_agent` with Gemini's built-in `google_search` | Gemini, written in `agent.py` | - |
| 03 | [`agent03_localmodel`](../agent03_localmodel/CASES.md) | `create_agent` | local, written in `agent.py` | - |
| 04 | [`agent04_localmodelwithtool`](../agent04_localmodelwithtool/CASES.md) | `create_agent` with a Python function as a tool | local, written in `agent.py` | - |
| 05 | [`agent05_state`](../agent05_state/CASES.md) | `create_agent` with a `state_schema` | local, written in `agent.py` | - |
| 06 | [`agent06_structured`](../agent06_structured/CASES.md) | `create_agent` with a `response_format` | local, written in `agent.py` | - |
| 07 | [`agent07_multiagent`](../agent07_multiagent/CASES.md) | A `StateGraph` whose nodes are three `create_agent` agents, joined by hand-off tools | switchable | - |
| 08 | [`agent08_workflow`](../agent08_workflow/CASES.md) | `StateGraph`, fixed order | switchable | - |
| 09 | [`agent09_parallel`](../agent09_parallel/CASES.md) | `StateGraph`, parallel nodes | switchable | - |
| 10 | [`agent10_loop`](../agent10_loop/CASES.md) | `StateGraph` with a conditional edge | switchable | - |
| 11 | [`agent11_guardrails`](../agent11_guardrails/CASES.md) | `create_agent` with middleware | switchable | - |
| 12 | [`agent12_mcp`](../agent12_mcp/CASES.md) | `create_agent`, built by an async `make_agent()` | switchable | `library_server.py` (the MCP server) |
| 13 | [`agent13_evals`](../agent13_evals/CASES.md) | `create_agent` | switchable | `bookshop.evalset.json`, `test_config.json`, `weak_config.json` |
| 14 | [`agent14_agent_as_tool`](../agent14_agent_as_tool/CASES.md) | `create_agent` that calls a second agent through a tool | switchable | - |

"switchable" means the model comes from `MODEL_PROVIDER`, or `AGENTNN_MODEL_PROVIDER` for that agent only.

## Notes on single agents

- **Agent 02** uses Google Search that runs on Google's side, so it is not an ordinary tool call. The chat
  runner prints the searches as `[google_search] [...]`.
- **Agent 06** returns an object, not text. The chat runner prints it as `[structured]: {...}`.
- **Agent 07** prints `[transfer] a -> b` at each hand-off. `/state` shows `active_agent`.
- **Agent 12** needs one terminal only: the agent starts the MCP server itself as a child process. You can
  also run the server alone with `uv run python agent12_mcp/library_server.py`.
- **Agent 13** is run with `uv run evals`, not chatted with. See [Evals and tests](evals-and-testing.md).

## Not ported yet

Agents 15 to 50 of the [Google ADK tutorial](../../google-adk-tutorial/README.md#the-agents). The shared
code for the RAG steps (`common/rag.py`, `common/embeddings.py`, `common/llm.py`, `data/handbook.md`) is
already here. [CONTRIBUTING.md](../CONTRIBUTING.md) describes how to port one.
