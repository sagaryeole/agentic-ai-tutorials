# Contributing

Thank you for helping with this tutorial. The most useful contribution right now is porting the next agent
from the [Google ADK tutorial](../google-adk-tutorial/README.md): agents 15 to 50 are still to come. Fixes
to a lesson, corrected "Expect" lines and clearer explanations are welcome too.

## Set up

    git clone https://github.com/sagaryeole/AgenticDemo.git
    cd AgenticDemo/langchain-adk-tutorial
    uv sync
    cp .env.example .env
    uv run pytest

[docs/getting-started.md](docs/getting-started.md) covers the model setup, and
[docs/architecture.md](docs/architecture.md) explains how this folder is put together.

## What makes a good lesson

- **One new idea.** If a change needs two new concepts, it is two lessons.
- **Same topic and cases as the ADK version.** A reader should be able to open both `CASES.md` files side by
  side. Where LangChain behaves differently, keep the case and say what differs.
- **Runs on both providers where possible.** Use `get_model()` so the reader can choose Gemini or a local
  model. If something only works on one, say so in `CASES.md`.
- **No outside services.** Tools return fixed demo data. If a lesson needs a server, ship a small one in the
  folder.
- **Claims are measured.** Write "Expect" lines from what you saw, and say which model produced it.
- **Plain language.** Explain a LangChain or LangGraph term the first time you use it.

## Porting an agent

1. Read the ADK lesson: `../google-adk-tutorial/agentNN_name/agent.py` and its `CASES.md`.
2. Create `agentNN_name/` here with the same name.
3. Add `__init__.py` containing `from . import agent`.
4. Add `agent.py` that defines a module-level `agent`:

   ```python
   from langchain.agents import create_agent
   from common.models import get_model  # global model switch, see common/models.py

   MODEL_KEY = "agentNN"  # lets AGENTNN_MODEL_PROVIDER override the global choice

   agent = create_agent(
       model=get_model(MODEL_KEY),
       name="root_agent",
       system_prompt="...",
       tools=[...],
   )
   ```

   If the agent needs async set-up, define `async def make_agent()` that returns it, as agent 12 does.
5. Add the agent to `langgraph.json`, so it appears in LangGraph Studio:
   `"agentNN_name": "./agentNN_name/agent.py:agent"` (or `:make_agent`).
6. Write `CASES.md` in the same shape as the others:
   - a first line `# agentNN_name: cases, easiest first`
   - the run command, the concept and the topic
   - `## How it executes` with a diagram, saying who decides what runs next (the model, or your code)
   - cases from easy to hard, each with the prompt, an `Expect:` line and a `Learn:` line
7. Add a row to the table in `README.md` and a link in exactly one learning track.
   `tests/test_readme_tracks.py` fails until you do.
8. If the port introduces a new ADK-to-LangChain translation, add it to the
   [concept map](README.md#from-adk-to-langchain).
9. Update the "ported so far" sentence in `README.md` and the table in
   [docs/agent-catalog.md](docs/agent-catalog.md). If the lesson has an environment switch or a port, add it
   to [docs/configuration.md](docs/configuration.md).

Check that `uv run chat agentNN_name` works, and `uv run langgraph dev` if you can.

## Writing tools

- Type every argument and write a docstring with an `Args:` section. The model reads both, so they are part
  of the prompt.
- Return a dict. On failure return `{"status": "error", "message": "..."}` with a message the model can
  pass on to the user.
- A tool that changes the conversation's state returns `Command(update={...})`, as agent 05 does.
- Keep secrets out of the prompt and out of the code. Read them from the environment.

## Changing shared code

`common/` is imported by every lesson from 07 on, and `common/chat.py` runs all of them, so keep changes
backwards compatible. `common/rag.py` and `tests/test_rag.py` are kept identical to the ADK tutorial's
copies; change both or neither. Tests must run without a model: replace model calls with a fake, as the
`fake_embeddings` fixture does.

## Before you open a pull request

- `uv run pytest` passes.
- You ran the cases you changed, ideally with `MODEL_PROVIDER=gemini` and `MODEL_PROVIDER=local`.
- No `.env`, `.langgraph_api/` folder, `*.db` file or personal data is in the commit. `.gitignore` already
  covers these.
- New dependencies are added with `uv add`, so `pyproject.toml` and `uv.lock` change together.
- The pull request says what the lesson teaches, or what was wrong, and on which model you tested.

## Reporting a problem

Open an issue at <https://github.com/sagaryeole/AgenticDemo/issues>. Include the command, the full error,
your `MODEL_PROVIDER` and the model name, and say that it is about the LangChain tutorial. Remove your
project id and any tokens first.

## License

The project is licensed under the [Apache License 2.0](LICENSE). By contributing, you agree that your
contribution is licensed under the same terms.
