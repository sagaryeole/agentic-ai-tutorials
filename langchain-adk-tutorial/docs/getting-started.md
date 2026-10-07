# Getting started

This page takes you from a fresh clone to a running agent. You need one of two model back ends, and you can
set up both:

| Back end | What you need | Used by |
|---|---|---|
| Gemini on Google Cloud (Vertex AI) | A Google Cloud project and the `gcloud` CLI | Agents 01 and 02 always; agents 07+ when `MODEL_PROVIDER=gemini` (the default) |
| A local model in [LM Studio](https://lmstudio.ai/) | A machine that can run a small model | Agents 03 to 06 always; agents 07+ when `MODEL_PROVIDER=local` |

Agents 01 and 02 only run on Gemini, and agents 03 to 06 only run on a local model, because those lessons
are about each back end. From agent 07 onwards you choose.

## 1. Install

The project uses [uv](https://docs.astral.sh/uv/), which installs the right Python (3.12, from
`.python-version`) and every package.

    git clone https://github.com/sagaryeole/AgenticDemo.git
    cd AgenticDemo/langchain-adk-tutorial
    uv sync

`uv sync` also installs the shared `common` package and two commands, `chat` and `evals`, into the virtual
environment. That is why `uv run chat ...` works from this folder.

## 2. Create your `.env`

    cp .env.example .env

One `.env` in the project root (this `langchain-adk-tutorial` folder) is enough: `common/models.py` loads
it, and every agent imports that module. `.env` is git-ignored; never commit it.

If you already have a `.env` from the Google ADK tutorial, you can copy it here. Its spelling
`GOOGLE_GENAI_USE_ENTERPRISE=1` is accepted too. Every variable is described in
[Configuration](configuration.md).

## 3a. Set up Gemini

Run these once, replacing `YOUR_PROJECT_ID`:

    gcloud auth login
    gcloud auth application-default login
    gcloud auth application-default set-quota-project YOUR_PROJECT_ID
    gcloud config set project YOUR_PROJECT_ID
    gcloud services enable aiplatform.googleapis.com

Then set `GOOGLE_CLOUD_PROJECT` in `.env` to the same project id.

## 3b. Set up a local model

1. Install LM Studio and download a chat model. The tutorial was written with `qwen3.5-9b`.
2. Open the Developer tab and start the server. It listens on `http://127.0.0.1:1234/v1`.
3. Find the model's exact id and put it in `.env` as `LOCAL_MODEL_ID`:

       curl http://127.0.0.1:1234/v1/models

Agents 03 to 06 have the model id `qwen3.5-9b` written in their `agent.py`. If you load a different model,
change it there for those four agents.

## 4. Run an agent

Chat in the terminal:

    uv run chat agent01_poet            # Gemini
    uv run chat agent03_localmodel      # LM Studio
    uv run chat agent07_multiagent      # whichever MODEL_PROVIDER says

While chatting, `/new` starts a new conversation, `/state` prints the conversation's state, and `exit`
quits. Add `--stream` to print the reply while it is being written.

Or start the local server and open LangGraph Studio in the browser, which draws the graph and shows each
step and the state:

    uv run langgraph dev

Studio is a web page hosted by LangChain that talks to the server on your machine. It may ask you to sign in
to a free LangSmith account.

Switch the model for one command, without editing anything:

    MODEL_PROVIDER=local  uv run chat agent08_workflow
    MODEL_PROVIDER=gemini uv run chat agent08_workflow

## 5. Check the installation without a model

The unit tests need no API key, no network and no LM Studio:

    uv run pytest

## What to do next

Open [agent01_poet/CASES.md](../agent01_poet/CASES.md) and work through the cases, then go on in order, or
pick a learning track from the [README](../README.md#learning-tracks). If you know Google ADK, keep the
[concept map](../README.md#from-adk-to-langchain) open. If a command fails, see
[Troubleshooting](troubleshooting.md).
