# Configuration

Everything is configured with environment variables. Put lasting choices in the root `.env` (copied from
`.env.example`) and one-off choices in front of the command:

    MODEL_PROVIDER=local uv run chat agent08_workflow

A variable set on the command line or in your shell wins over `.env`.

## Google Cloud

Needed by agents 01 and 02, by agents 07+ when `MODEL_PROVIDER=gemini`, by Gemini embeddings, and by the
judge model of the evals unless you change `JUDGE_PROVIDER`.

| Variable | Value in `.env.example` | Meaning |
|---|---|---|
| `GOOGLE_GENAI_USE_VERTEXAI` | `true` | Use Gemini through Google Cloud (Vertex AI) with your `gcloud` login, not an API key |
| `GOOGLE_CLOUD_PROJECT` | `your-gcp-project-id` | Your project id. You must change this. |
| `GOOGLE_CLOUD_LOCATION` | `global` | The region to call |

`GOOGLE_GENAI_USE_ENTERPRISE`, the spelling in the ADK tutorial's `.env`, is accepted as well:
`common/models.py` turns it into `GOOGLE_GENAI_USE_VERTEXAI=true`.

## Chat model

Read by `common/models.py`.

| Variable | Default in code | Meaning |
|---|---|---|
| `MODEL_PROVIDER` | `gemini` | `gemini` or `local`. The global switch. |
| `AGENTNN_MODEL_PROVIDER` | not set | Overrides `MODEL_PROVIDER` for one agent, for example `AGENT10_MODEL_PROVIDER=gemini` |
| `GEMINI_MODEL` | `gemini-2.5-flash` | The Gemini model name |
| `LOCAL_MODEL_ID` | `qwen3.5-9b` | The model id LM Studio reports at `/v1/models` |
| `LOCAL_API_BASE` | `http://127.0.0.1:1234/v1` | The address of the OpenAI-compatible server |
| `LOCAL_API_KEY` | `lm-studio` | The key sent to the local server. LM Studio accepts any value. |

Agents 01 to 06 ignore all of these: their model is written in `agent.py`.

## Evals

| Variable | Default in code | Meaning |
|---|---|---|
| `JUDGE_PROVIDER` | `gemini` | `gemini` or `local`. The model that grades answers for the `response_judge` check. It can differ from the model under test. |

## Embeddings

Read by `common/embeddings.py`. No ported agent uses embeddings yet; they are here for the RAG steps that
come next.

| Variable | Default in code | Meaning |
|---|---|---|
| `EMBEDDING_PROVIDER` | `gemini` | `gemini` or `local` |
| `GEMINI_EMBEDDING_MODEL` | `text-embedding-005` | The Gemini embedding model |
| `LOCAL_EMBEDDING_MODEL` | `text-embedding-embeddinggemma-300m` | The embedding model id loaded in LM Studio |

`.env.example` sets `EMBEDDING_PROVIDER=local`, so copying it unchanged selects local embeddings.

## `uv run chat`

    uv run chat <agent folder> [--user NAME] [--set KEY=VALUE ...] [--stream]

| Option | Default | Meaning |
|---|---|---|
| `--user` | `student` | Who is chatting (the user id) |
| `--set KEY=VALUE` | none | A value for the agent's context, for an agent that defines a `context_schema`. Repeat for more. |
| `--stream` | off | Print the reply while it is being written |

While chatting: `/new` starts a new conversation, `/state` prints the conversation's state, `exit` or
`quit` ends the program.

## `uv run evals`

    uv run evals <agent folder> <evalset.json>[:case_id[,case_id]] --config <config.json> [--details] [--set KEY=VALUE ...]

| Option | Meaning |
|---|---|
| `:case_id` | Run only the named case or cases |
| `--config` | The file with the checks and their thresholds. Required. |
| `--details` | Print the tool calls, the answer and the judge's reason for every case. Failed cases always show them. |
| `--set KEY=VALUE` | A value for the agent's context |

Exit code: `0` when every case passed, `1` when any failed, `2` when no case matched the name.

## `langgraph.json`

`uv run langgraph dev` serves the graphs listed in this file.

| Key | Meaning |
|---|---|
| `dependencies` | `["."]`: install this project, so `common` can be imported |
| `graphs` | One entry per agent: `"<name>": "./<folder>/agent.py:<attribute>"`. The attribute is `agent`, or `make_agent` for an agent that is built by a function (agent 12). |
| `env` | `.env`: the file the server loads |

An agent that is not listed here does not appear in Studio.

## Ports

| Port | Service | Started by |
|---|---|---|
| 1234 | LM Studio's OpenAI-compatible server | LM Studio, Developer tab |

`uv run langgraph dev` prints its own address when it starts.

## Secrets

- `.env` is ignored by git and by `.dockerignore`. Keep it that way.
- The Google setup uses your `gcloud` login, so there is no API key to store.
