# Evals and tests

| Kind | Command | Needs a model | Answers |
|---|---|---|---|
| Unit tests | `uv run pytest` | No | Is the shared code correct, and is the README consistent? |
| Evals | `uv run evals ...` | Yes | Does this agent still call the right tools and give the right answer? |

## Unit tests

    uv run pytest

Runs in under a second with no API key, no network and no LM Studio.

| File | Checks |
|---|---|
| `tests/test_rag.py` | `common/rag.py`: the four chunkers, tokens and keyword overlap, BM25, ranking, rank fusion, and `Index.search`. The embedding model is replaced by a small deterministic fake. |
| `tests/test_readme_tracks.py` | Every `agentNN_*` folder has a `CASES.md` and is linked from exactly one learning track in the README |

The second test fails if you add an agent folder and forget to link it.

## Evals

LangChain has no `eval` command of its own. Hosted tools (LangSmith) and libraries (agentevals, openevals)
offer ready-made checks; `common/evals.py` is the same idea, small enough to read in one sitting.

    uv run evals agent13_evals agent13_evals/bookshop.evalset.json \
        --config agent13_evals/test_config.json

It loads the agent, plays each case to it in a new thread, and prints `PASSED` or `FAILED` per case with
the scores. Cases run one after another, so a local model is not asked to do several things at once.

### The eval set

A JSON file with cases. A case is a conversation of one or more turns:

```json
{
  "name": "Bookshop basics",
  "cases": [
    {
      "id": "book_details",
      "turns": [
        {
          "user": "Tell me about book B003.",
          "expected_tools": [{"name": "get_book", "args": {"book_id": "B003"}}],
          "reference": "Book B003 is Dune by Frank Herbert, published in 1965. It is available."
        }
      ]
    }
  ]
}
```

`expected_tools` is optional. When it is left out and the `tool_trajectory` check is on, the agent is
expected to call no tools in that turn.

### The config

Names the checks and the score each one needs:

```json
{ "criteria": { "tool_trajectory": 1.0, "response_judge": 0.8 } }
```

| Check | Score | Uses a model |
|---|---|---|
| `tool_trajectory` | `1.0` if the agent called exactly the expected tools with exactly the expected arguments, in order; else `0.0` | No |
| `response_judge` | `1.0` if a second model, the judge, says the answer agrees with the reference; else `0.0` | Yes, one call per turn |
| `response_overlap` | The share of words the answer and the reference have in common (ROUGE-1), from 0 to 1 | No |

A case passes when, for every check, the average over its turns reaches the threshold.

Agent 13 ships two configs so you can compare them: `test_config.json` (trajectory plus the judge) and
`weak_config.json` (trajectory plus word overlap, which cannot tell "is available" from "is not available").

### Options

- `--details` prints the tool calls, the answer and the judge's reason for every case. Failed cases always
  show them.
- Append `:case_id` to the eval set path to run one case, or several separated by commas:
  `agent13_evals/bookshop.evalset.json:book_details`.
- Prefix the command with `MODEL_PROVIDER=local` or `MODEL_PROVIDER=gemini` to choose the model under test.
- `JUDGE_PROVIDER=local` makes the local model the judge. The default judge is Gemini, so by default you
  need the Google Cloud settings even when the agent under test is a local model.
- The command exits with `0` when every case passed and `1` otherwise, so a build script can use it.

A model can answer differently on each run, so one failing case is not always a regression. Run it again
with `--details` before you conclude anything.

[agent13_evals/CASES.md](../agent13_evals/CASES.md) teaches how to write cases and pick checks.

### How this differs from `adk eval`

| | Google ADK | Here |
|---|---|---|
| Command | `adk eval <agent> <evalset> --config_file_path <config>` | `uv run evals <agent> <evalset> --config <config>` |
| Per-case output | `--print_detailed_results` | `--details` |
| Tool check | `tool_trajectory_avg_score` | `tool_trajectory` |
| LLM judge | `final_response_match_v2` | `response_judge` |
| Word overlap | `response_match_score` | `response_overlap` |
| File format | ADK's evalset schema | The smaller schema shown above |

The files are not interchangeable between the two tutorials.

## Before you send a change

    uv run pytest

Then run the cases of any lesson you touched, on both providers if you can. If a result differs from an
"Expect" line, update the line to say what you saw and on which model.
