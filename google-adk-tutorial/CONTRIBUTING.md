# Contributing

Thank you for helping with this tutorial. Fixes to a lesson, corrected "Expect" lines, clearer
explanations and new agents are all welcome.

## Set up

    git clone https://github.com/sagaryeole/AgenticDemo.git
    cd AgenticDemo/google-adk-tutorial
    uv sync
    cp .env.example .env
    uv run pytest

[docs/getting-started.md](docs/getting-started.md) covers the model setup, and
[docs/architecture.md](docs/architecture.md) explains how the repository is put together.

## What makes a good lesson

The tutorial works because each folder is small and adds one thing.

- **One new idea.** If a change needs two new concepts, it is two lessons.
- **Runs on both providers where possible.** Use `get_model()` so the reader can choose Gemini or a local
  model. If something only works on one, say so in `CASES.md` and fail at start-up with a clear message.
- **No outside services.** Tools return fixed demo data. If a lesson needs a server, ship a small one in the
  folder.
- **Claims are measured.** Write "Expect" lines from what you saw, and say which model produced it. If the
  lesson claims that one approach beats another, add a script that counts it.
- **Plain language.** The reader may be new to agents. Explain a term the first time you use it.

## Adding an agent

1. Create `agentNN_shortname/` with the next free number.
2. Add `__init__.py` containing `from . import agent`.
3. Add `agent.py` that defines `root_agent`:

   ```python
   from google.adk.agents import Agent
   from common.models import get_model  # global model switch, see common/models.py

   MODEL_KEY = "agentNN"  # lets AGENTNN_MODEL_PROVIDER override the global choice

   root_agent = Agent(
       name="root_agent",
       model=get_model(MODEL_KEY),
       description="One line saying what this agent is for.",
       instruction="...",
   )
   ```

4. Write `CASES.md` in the same shape as the others:
   - a first line `# agentNN_shortname: cases, easiest first`
   - the run command, the concepts and the topic
   - `## How it executes` with a diagram, saying who decides what runs next (the model, or your code)
   - cases from easy to hard, each with the prompt, an `Expect:` line and a `Learn:` line
5. Add a row to the table in `README.md` and a link in exactly one learning track.
   `tests/test_readme_tracks.py` fails until you do.
6. If the lesson has an environment switch, a port or a helper script, add it to
   [docs/configuration.md](docs/configuration.md) and [docs/agent-catalog.md](docs/agent-catalog.md).
7. If it fits a module of [questions.md](questions.md), add a short section and a question or two.

A lab (a script with no agent) follows the same steps without `agent.py`.

## Writing tools

- Type every argument and write a docstring with an `Args:` section. ADK shows both to the model, so they
  are part of the prompt.
- Return a dict. On failure return `{"status": "error", "message": "..."}` with a message the model can
  pass on to the user.
- Keep secrets out of the prompt and out of the code. Read them from the environment, as agent 41 does.

## Changing shared code

`common/` is imported by most lessons, so keep changes backwards compatible and add a test to
`tests/test_rag.py` when you touch `common/rag.py`. Tests must run without a model: replace model calls with
a fake, as the `fake_embeddings` fixture does.

## Before you open a pull request

- `uv run pytest` passes.
- You ran the cases you changed, ideally with `MODEL_PROVIDER=gemini` and `MODEL_PROVIDER=local`.
- No `.env`, `.adk/` folder, `*.db` file, session file or personal data is in the commit. `.gitignore`
  already covers these; check `git status` if you added new kinds of output.
- New dependencies are added with `uv add`, so `pyproject.toml` and `uv.lock` change together.
- The pull request says what the lesson teaches, or what was wrong, and on which model you tested.

## Reporting a problem

Open an issue at <https://github.com/sagaryeole/AgenticDemo/issues>. Include the command, the full error,
your `MODEL_PROVIDER` and the model name. Remove your project id and any tokens first.

## License

The project is licensed under the [Apache License 2.0](LICENSE). By contributing, you agree that your
contribution is licensed under the same terms.
