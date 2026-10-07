# Evals and tests

The repository checks itself in three ways. They answer different questions, so it helps to know which one
you are running.

| Kind | Command | Needs a model | Answers |
|---|---|---|---|
| Unit tests | `uv run pytest` | No | Is the shared code correct, and is the README consistent? |
| ADK evals | `uv run adk eval ...` | Yes | Does this agent still call the right tools and give the right answer? |
| Measuring scripts | `uv run python agentNN_.../script.py` | Yes | How often does this behaviour happen? |

## Unit tests

    uv run pytest

Runs in well under a second with no API key, no network and no LM Studio.

| File | Checks |
|---|---|
| `tests/test_rag.py` | `common/rag.py`: the four chunkers, tokens and keyword overlap, BM25, ranking, rank fusion, and `Index.search`. The embedding model is replaced by a small deterministic fake. |
| `tests/test_readme_tracks.py` | Every `agentNN_*` folder has a `CASES.md` and is linked from exactly one learning track in the README |

The second test fails if you add an agent folder and forget to link it. See
[Contributing](../CONTRIBUTING.md).

## ADK evals

An evalset is a JSON file of recorded conversations: the user's messages, the tool calls that should
happen, and a reference answer. `adk eval` replays them against the agent and scores the result using the
criteria in a config file.

    uv run adk eval agent13_evals agent13_evals/bookshop.evalset.json \
        --config_file_path agent13_evals/test_config.json

| Agent | Evalset | Config files |
|---|---|---|
| 13 | `bookshop.evalset.json` | `test_config.json` (tool trajectory plus an LLM judge), `weak_config.json` (word overlap, to show why it is weaker) |
| 20 | `rag.evalset.json` | `rag_config.json` |
| 25 | `lunch.evalset.json` | `multiturn_config.json`, `rubric_config.json` |
| 50 | `library.evalset.json` | `eval_config.json` |

Useful options:

- `--print_detailed_results` prints the score of every case.
- Append `:case_name` to the evalset path to run one case:
  `agent13_evals/bookshop.evalset.json:book_details`.
- Prefix the command with `MODEL_PROVIDER=local` or `MODEL_PROVIDER=gemini` to choose the model under test.

Things to know:

- The `final_response_match_v2` criterion uses an LLM as the judge, and the judge runs on Gemini. You need
  the Google Cloud settings even when the agent under test is a local model.
- `adk eval` does not put the project folder on the import path. `from common...` still works because
  `uv sync` installs `common` into the virtual environment.
- Results are saved under `<agent>/.adk/eval_history/`, which is git-ignored.
- A model can answer differently on each run, so one failing case is not always a regression. Run it again
  before you conclude anything.

[agent13_evals/CASES.md](../agent13_evals/CASES.md) and
[agent25_multiturn_evals/CASES.md](../agent25_multiturn_evals/CASES.md) teach how to write evalsets and
pick criteria.

## Measuring scripts

Some lessons make a claim such as "a rule enforced in code holds where a rule in the prompt does not". Those
folders ship a script that runs the agent many times and counts what really happened, usually by checking
stored data and not the wording of the reply.

    PERMISSION_MODE=prompt uv run python agent48_permissions/permission_test.py
    PERMISSION_MODE=code   uv run python agent48_permissions/permission_test.py

The full list is in the [agent catalog](agent-catalog.md#lessons-with-a-measuring-script). They call a real
model, so they take time and, on Gemini, cost money. Several accept `--repeats` to trade time for
confidence.

The labs (16 to 19, 35, 36, 39, 49) are measuring scripts with no agent at all. Lab 36 is the one to read
for evaluating a RAG pipeline: it scores retrieval and the final answer separately, so you can tell which
step is weak.

## Before you send a change

    uv run pytest

Then run the cases of any lesson you touched, on both providers if you can. If a result differs from an
"Expect" line, update the line to say what you saw and on which model.
