# Troubleshooting

## Gemini

**`API key required for Gemini Developer API`**

The Google settings are missing. Check that `.env` exists in the project root and contains
`GOOGLE_GENAI_USE_VERTEXAI`, `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`, with your real project id.
See [Configuration](configuration.md#google-cloud).

**A permission or credentials error**

Run the `gcloud` commands in [Getting started](getting-started.md#3a-set-up-gemini) again. The two that are
most often missed are `gcloud auth application-default login` (a different login from `gcloud auth login`)
and `gcloud services enable aiplatform.googleapis.com`.

**`429 RESOURCE_EXHAUSTED`**

Gemini received too many calls in a short time. Agents 07+ already retry (`max_retries=6` in
`common/models.py`). If it still fails, wait a minute and try again.

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
which often describe what the local model did.

## Running

**`uv run chat` says the command was not found**

Run `uv sync` in this folder. It installs the `chat` and `evals` commands that `pyproject.toml` defines.

**`ModuleNotFoundError` for an agent folder**

`uv run chat` imports the folder relative to the current directory. Run it from the project root, and pass
the folder name only: `uv run chat agent07_multiagent`.

**`ModuleNotFoundError: No module named 'common'`**

Run `uv sync`, and start commands with `uv run` so they use the project's virtual environment.

**A setting has no effect**

The provider is read once, when the agent is imported. Quit the chat, or stop `langgraph dev`, and start
again.

**The agent forgot the conversation after I restarted the chat**

That is expected. The chat runner keeps conversations in memory. `/new` starts a new one on purpose.

**An agent does not appear in LangGraph Studio**

Studio shows the graphs listed in `langgraph.json`. Add an entry for the agent; see
[Configuration](configuration.md#langgraphjson).

**Studio asks me to sign in**

Studio is a web page hosted by LangChain that connects to the server on your machine. It may ask for a free
LangSmith account. The terminal chat needs no account.

## Evals

**The eval fails with a Gemini error although I test a local model**

The judge model is Gemini by default. Set up Google Cloud, or use `JUDGE_PROVIDER=local`.

**`No case named ...`**

The name after the colon must match a case `id` in the eval set file.

**An eval fails once and passes the next time**

See [Evals and tests](evals-and-testing.md#options).

## Results

**My result differs from the "Expect" line**

Model output varies between runs, between Gemini and the local model, and between model versions. The
"Expect" lines record what happened when the case was tested. If the lesson's point still holds, nothing is
wrong. If it does not, that is worth an issue.

## Still stuck

Open an issue at <https://github.com/sagaryeole/AgenticDemo/issues> with the command you ran, the full
error, your `MODEL_PROVIDER`, and the model name. Say that it is about the LangChain tutorial. Remove your
project id and any tokens first.
