# Configuration

Everything is configured with environment variables. Put lasting choices in the root `.env` (copied from
`.env.example`) and one-off choices in front of the command:

    MODEL_PROVIDER=local uv run adk run agent08_workflow

A variable set on the command line or in your shell wins over `.env`.

## Google Cloud

Needed by agents 01 and 02, by agents 07+ when `MODEL_PROVIDER=gemini`, by Gemini embeddings, and by the
LLM judge that `adk eval` uses.

| Variable | Value in `.env.example` | Meaning |
|---|---|---|
| `GOOGLE_GENAI_USE_ENTERPRISE` | `1` | Use Gemini through Google Cloud (Vertex AI) with your `gcloud` login, not an API key |
| `GOOGLE_CLOUD_PROJECT` | `your-gcp-project-id` | Your project id. You must change this. |
| `GOOGLE_CLOUD_LOCATION` | `global` | The region to call |

## Chat model

Read by `common/models.py` (agents 07+) and `common/llm.py` (labs).

| Variable | Default in code | Meaning |
|---|---|---|
| `MODEL_PROVIDER` | `gemini` | `gemini` or `local`. The global switch. |
| `AGENTNN_MODEL_PROVIDER` | not set | Overrides `MODEL_PROVIDER` for one agent, for example `AGENT10_MODEL_PROVIDER=gemini`. Only applies to agents built with `get_model()`; `ask()` in the labs follows `MODEL_PROVIDER` only. |
| `GEMINI_MODEL` | `gemini-2.5-flash` | The Gemini model name |
| `LOCAL_MODEL_ID` | `qwen3.5-9b` | The model id LM Studio reports at `/v1/models` |
| `LOCAL_API_BASE` | `http://127.0.0.1:1234/v1` | The address of the OpenAI-compatible server |
| `LOCAL_API_KEY` | `lm-studio` | The key sent to the local server. LM Studio accepts any value. |

Agents 01 to 06 ignore all of these: their model is written in `agent.py`.

## Embeddings

Read by `common/embeddings.py`. Used by labs 17 to 19, 35, 36 and 49, and by agents 20, 37, 38 and 50.

| Variable | Default in code | Meaning |
|---|---|---|
| `EMBEDDING_PROVIDER` | `gemini` | `gemini` or `local` |
| `GEMINI_EMBEDDING_MODEL` | `text-embedding-005` | The Gemini embedding model |
| `LOCAL_EMBEDDING_MODEL` | `text-embedding-embeddinggemma-300m` | The embedding model id loaded in LM Studio |

Two things to know:

- `.env.example` sets `EMBEDDING_PROVIDER=local` and its own `GEMINI_EMBEDDING_MODEL`. Copying it unchanged
  therefore gives you local embeddings, which need an embedding model loaded in LM Studio. Remove those
  lines to fall back to the defaults in the table.
- When `EMBEDDING_PROVIDER` is not set at all, agents 20 and 50 make it follow their chat provider, so
  `MODEL_PROVIDER=local` gives a fully local agent.

Vectors from different models are not comparable. If you change the provider or the model, restart the
process so the index is rebuilt.

## Per-agent switches

These exist so a case can show an idea with and without one piece. The values listed are the ones the cases
use; each agent's `CASES.md` explains what they do.

| Agent | Variable | Default | Values used in the cases |
|---|---|---|---|
| 21 | `MEMORY_FILE` | `agent21_memory/memory.json` | a file path |
| 22 | `CODE_MODE` | `builtin` on Gemini, `calculator` on local | `builtin`, `calculator`, `none` |
| 24 | `PLANNER_MODE` | `thinking` on Gemini, `default` on local | `default`, `no_thinking`, `thinking`, `plan_react` (set by `evaluate.py --mode`). The two thinking modes need Gemini. |
| 24 | `CHECKER` | `off` | `on` (set by `evaluate.py --tool on`) |
| 24 | `SHOW_REPLY` | not set | any value: `evaluate.py` prints each reply |
| 25 | `FORGET_HISTORY` | not set | `1` |
| 26 | `OBS_LOGGING`, `OBS_SPANS` | not set | `1` |
| 27 | `SHIPPING_AGENT_URL` | `http://localhost:8001` | the address of the remote agent |
| 29 | `FEW_SHOT` | `1` | `0` |
| 29 | `SHOW_INSTRUCTION` | not set | `1` |
| 30 | `CONTEXT_MODE` | `full` | `full`, `trim`, `compact` (set by `long_chat.py --mode`) |
| 31 | `DEFENSE` | `layers` | `none`, `prompt`, `layers` (set by `attack_test.py --defense`) |
| 31 | `FULL_REPLY` | not set | `1`: `attack_test.py` prints whole replies |
| 38 | `TOOL_MODE` | `all` | `all`, `routed`, `vague` |
| 38 | `TOP_N` | `4` | `1`, `2`, `4` |
| 40 | `PRIMARY_PROVIDER` | `gemini` | `gemini`, `local` |
| 40 | `BREAK_PRIMARY` | `none` | `down`, `slow` |
| 40 | `TIMEOUT_SECONDS` | `60` | seconds |
| 40 | `SLOW_TOOL` | not set | `1` |
| 41 | `NOTES_API_TOKEN` | a made-up demo value | the token shared by the notes service and the agent |
| 41 | `AUTH_MODE` | `bearer` | `bearer`, `none`, `wrong` |
| 41 | `LEAK` | not set | `1` |
| 45 | `ANALYSIS_MODE` | `tools` | `tools`, `code`, `none` |
| 46 | `FLAKY` | not set | `1` |
| 48 | `PERMISSION_MODE` | `code` | `code`, `prompt`, `weak` |
| 50 | `NOTICE_FILTER` | `on` | `off` |

Most of these are read once, when the agent module is imported. Set them before starting `adk run` or
`adk web`; changing them needs a restart.

## Ports

| Port | Service | Started by |
|---|---|---|
| 1234 | LM Studio's OpenAI-compatible server | LM Studio, Developer tab |
| 8001 | Remote shipping agent (A2A) | `uv run uvicorn agent27_a2a.remote_server:a2a_app --port 8001` |
| 8002 | To-do REST API | `uv run uvicorn agent32_openapi_tools.todo_api:api --port 8002` |
| 8003 | Notes REST API with a bearer token | `uv run uvicorn agent41_tool_auth.notes_api:api --port 8003` |
| 8004 | Agent 44 behind `adk api_server` | `uv run adk api_server --port 8004 agent44_serving` |
| 8005 | The capstone behind `adk api_server` | see [agent50_capstone/CASES.md](../agent50_capstone/CASES.md) |
| 8080 | Agent 44 in a container | `agent44_serving/Dockerfile` |

`uv run adk web` prints its own address when it starts.

## Secrets

- `.env` is ignored by git and by `.dockerignore`. Keep it that way.
- The Google setup uses your `gcloud` login, so there is no API key to store.
- `NOTES_API_TOKEN` has a made-up default so agent 41 runs out of the box. It is not a real secret.
- The Dockerfile for agent 44 copies no `.env` into the image; pass settings with `docker run -e`.
