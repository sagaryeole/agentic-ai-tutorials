# Troubleshooting

## Gemini

**`No API key was provided`**

The Google settings are missing. Check that `.env` exists in the project root and contains
`GOOGLE_GENAI_USE_ENTERPRISE`, `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`, with your real project
id. See [Configuration](configuration.md#google-cloud).

**A permission or credentials error**

Run the `gcloud` commands in [Getting started](getting-started.md#3a-set-up-gemini) again. The two that are
most often missed are `gcloud auth application-default login` (a different login from `gcloud auth login`)
and `gcloud services enable aiplatform.googleapis.com`.

**`429 RESOURCE_EXHAUSTED`**

Gemini received too many calls in a short time. Agents 07+ and the labs already retry (6 attempts, waiting
up to 60 seconds). If it still fails, wait a minute. Parallel agents, evals and the measuring scripts are the
usual cause; lower `--repeats` or `--concurrency`.

**Agents 01 and 02 ignore `MODEL_PROVIDER`**

That is intended. Their model is written in `agent.py`, and agent 02's `google_search` tool only exists on
Gemini.

## Local model

**Connection refused on `127.0.0.1:1234`**

The LM Studio server is not running. Open the Developer tab and start it, then check:

    curl http://127.0.0.1:1234/v1/models

**The server answers, but the model is not found**

`LOCAL_MODEL_ID` must match an id from that `curl` output exactly. Agents 03 to 06 do not read
`LOCAL_MODEL_ID`: the id `qwen3.5-9b` is written in their `agent.py`, so edit it there if you use another
model.

**The local model does not call tools, or calls them badly**

Small models differ a lot here. Use a model that supports tool calling, and compare with the "Expect" lines,
which often describe what the local model did. Module 11 of [questions.md](../questions.md) compares Gemini
and the small local model across the tutorial.

**An embedding error with `EMBEDDING_PROVIDER=local`**

Load an embedding model in LM Studio as well as the chat model, and set `LOCAL_EMBEDDING_MODEL` to its id.
Note that `.env.example` selects local embeddings; see [Configuration](configuration.md#embeddings).

## A mode that needs Gemini

Some switches stop at start-up with a clear message when the provider cannot do what was asked: for
example `CODE_MODE=builtin` (agent 22), `ANALYSIS_MODE=code` (agent 45) and the thinking modes of agent 24.
Use the mode the message suggests, or run that agent on Gemini:

    AGENT22_MODEL_PROVIDER=gemini uv run adk run agent22_code_execution

## Running

**A setting has no effect**

Most switches are read once, when the agent is imported. Stop `adk run` or `adk web` and start it again.
Also check for a `.env` inside the agent's folder: ADK finds that one before the root file.

**`adk web` does not list the agents**

Start it from the project root, not from inside an agent folder.

**`ModuleNotFoundError: No module named 'common'`**

Run `uv sync`, and start commands with `uv run` so they use the project's virtual environment.

**Connection refused on port 8001 to 8005**

That lesson needs a server in a second terminal. See the
[agent catalog](agent-catalog.md#lessons-that-need-a-second-terminal).

**`Address already in use`**

An earlier server is still running on that port. Stop it, or pass another `--port` (and for agent 27, set
`SHIPPING_AGENT_URL` to match).

**An agent remembers something from an earlier run**

Some agents keep data on disk on purpose: `agent21_memory/memory.json`,
`agent34_persistent_sessions/sessions.db`, and `agent50_capstone/library.db` when the capstone is started with
`--session_service_uri`. Delete the file to start clean.

## Results

**My result differs from the "Expect" line**

Model output varies between runs, between Gemini and the local model, and between model versions. The
"Expect" lines record what happened when the case was tested. If the lesson's point still holds, nothing is
wrong. If it does not, that is worth an issue.

**An eval fails once and passes the next time**

See [Evals and tests](evals-and-testing.md#adk-evals).

## Docker

`agent44_serving/Dockerfile` says in its first lines that it was not tested when it was written. Treat it as
a starting point. Build it from the project root, because the agent imports `common`.

## Still stuck

Open an issue at <https://github.com/sagaryeole/AgenticDemo/issues> with the command you ran, the full
error, your `MODEL_PROVIDER`, and the model name. Remove your project id and any tokens first.
