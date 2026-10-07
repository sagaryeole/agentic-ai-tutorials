# agent13_evals: cases, easiest first

Concept: evals. Instead of typing questions by hand and eyeballing the answers, you write the questions
and the expected behaviour down once, and a runner plays them to the agent and scores the result.
Topic: a bookshop assistant (`agent.py`) tested by 6 eval cases (`bookshop.evalset.json`).

Files:
- `agent.py`: the agent being tested (function tools over a 5-book catalogue).
- `bookshop.evalset.json`: the test cases. Each has a question, the expected tool call, and a reference answer.
- `test_config.json`: how to score. Tool calls must match exactly, and an LLM judge compares the answer to the reference.
- `weak_config.json`: the same, but with a word-overlap score instead of the judge. Used in case 5 to show a blind spot.
- `common/evals.py` (shared): the runner. LangChain has no `eval` command of its own, so this tutorial has a small one you can read.
  Hosted tools (LangSmith) and libraries (`agentevals`, `openevals`) offer ready-made versions of the same checks.

## Run it
From the project root:

    uv run evals agent13_evals agent13_evals/bookshop.evalset.json \
        --config agent13_evals/test_config.json

- Add `--details` for the tool calls, the answer and the judge's reason of every case (failed cases always show them).
  Prefix with `MODEL_PROVIDER=local` or `gemini` to pick the agent's model.
- Run one case: `agent13_evals/bookshop.evalset.json:book_details`.
- The judge is a second model. It uses Gemini even when the agent runs on the local model, so the Google settings must be set.
  `JUDGE_PROVIDER=local` makes the local model the judge instead.
- The command exits with code 0 when every case passed and 1 otherwise, so a build script can use it.

## How it executes
Control: the eval runner drives the agent, you do not. For each case it plays the question to the real
agent, records what the agent did, and compares that to what you wrote down.

```
 bookshop.evalset.json                          test_config.json
 ┌─────────────────────────────────┐            ┌──────────────────────────────┐
 │ case: book_details              │            │ tool_trajectory   1.0        │
 │  user:  "Tell me about B003"    │            │ response_judge    0.8        │
 │  expected_tools: get_book(B003) │            └───────────────┬──────────────┘
 │  reference: "...Dune..."        │                            │ thresholds
 └───────────────┬─────────────────┘                            │
                 │ question                                     │
                 ▼                                              │
         ┌───────────────┐   runs the real agent (a real model call)
         │ agent13_evals │──► actual tool calls  + actual answer
         └───────────────┘             │                  │
                                       ▼                  ▼
                        ┌──────────────────────┐  ┌────────────────────────┐
                        │ trajectory check     │  │ answer check           │
                        │ same tool, same args?│  │ judge model: does it   │
                        │ (exact, in code)     │  │ mean the same thing?   │
                        └──────────┬───────────┘  └───────────┬────────────┘
                                   └────────► score vs threshold ◄───┘
                                                    │
                                              PASSED / FAILED per case
```

## Case 1: run the evals
Run the command above, on both models.

Expect: `Tests passed: 6`, `Tests failed: 0` on both Gemini and the local `qwen3.5-9b` (what happened in testing).
Learn: one command replaces typing six questions by hand, and gives a pass/fail you can repeat.

## Case 2: read what is being checked
Open `bookshop.evalset.json` and look at `author_search`.
Expect: the question, the tool it must call (`find_books_by_author` with `{"author": "Tolkien"}`),
and a reference answer.
Learn: there are two separate things to test. Did the agent take the right action (tool trajectory)?
Did it say the right thing (final response)?

## Case 3: the trajectory check catches a wrong tool
In `bookshop.evalset.json`, change the expected tool for `unavailable_book` from `get_book` with
`{"book_id": "B005"}` to `list_books` with `{}`. Run again.
Expect: 5 passed, 1 failed (`unavailable_book`), with `tool_trajectory` at 0.00.
Learn: the check compares tool names and arguments exactly. Revert the edit afterwards.

## Case 4: a case where the agent must NOT call a tool
Look at `no_tool_needed` ("What is a library?").
Expect: its expected tool list is empty, so it fails if the agent calls any tool.
Learn: tests should cover when the agent should stay quiet too, not only when it should act.

## Case 5: the word-overlap metric has a blind spot
Change the reference answer of `unavailable_book` to claim the opposite:
`"Yes, book B005, Foundation by Isaac Asimov, is available."` (B005 is NOT available). Then run twice:

    ... --config agent13_evals/weak_config.json    # word overlap (ROUGE)
    ... --config agent13_evals/test_config.json    # LLM judge

Expect: with the weak config the case still PASSES (the overlap is high, because nearly every word matches: an answer that says
exactly the opposite of that reference scores 0.84). With the judge config it FAILS (score 0.00).
Learn: a metric that counts shared words cannot tell "is available" from "is not available". Choose the metric
for what you care about. Judge metrics understand meaning but cost a model call. Revert the edit afterwards.

## Case 6: would an eval have caught the agent12 bug?
Agent12's case 8 describes a `list_books` without the `available` field, where a model guessed "Available" for every book.
Here the case `list_with_availability` guards against that. Reproduce the bug: in `agent.py` remove
`"available": b["available"]` from `list_books`, then run just that case:

    ... bookshop.evalset.json:list_with_availability --config agent13_evals/test_config.json --details

Expect: the case FAILS, but how depends on the model. One model keeps to `list_books` and guesses the availability
(trajectory passes, judge fails). Another notices the missing information and calls `get_book` for each book instead:
right answer by a different route (judge passes, trajectory fails).
Learn: a failing eval tells you something changed;
you still read the details to see if the answer or just the route is different. Restore the field afterwards.

## Case 7: same tests, different model
Run case 1 with `MODEL_PROVIDER=gemini` and again with `MODEL_PROVIDER=local`.
Expect: both pass here. A weaker model may fail some cases, for example by picking another tool or arguments.
Learn: an eval set is a way to compare models, and to check that switching models did not break anything.

## Case 8: exact arguments are strict
The arguments must match exactly. Edit `author_search` to expect `{"author": "J.R.R. Tolkien"}` and run it a few times.
Expect: it fails. The question says "Tolkien", the model passes
`Tolkien`, and the full name never appears. The test was wrong here, not the agent.
Learn: an eval can fail because your expectation is off. Free-text arguments are also where a model may
vary between runs, for example "Tolkien" one time and "J.R.R. Tolkien" another, so write questions that make
the expected argument obvious, or relax the check. Revert afterwards.

## Case 9: the judge is a prompt too
Read `JUDGE_INSTRUCTION` in `common/evals.py`.
Learn: the first version of that instruction called an answer invalid when any fact of the reference was "missing". The local
agent answered "Is book B005 available?" with "No, book B005 is not available.", and the judge failed it for not repeating
the title and the author. The answer was fine; the judge was too strict. A judge is a model following your instruction, so
it needs the same care, and the same testing, as the agent it grades.

## Case 10: what evals do not do
Evals test the cases you wrote. They do not cover questions you did not think of.
Learn: they are a safety net for known behaviour, and each new bug is a good reason to add a case.
That is how `list_with_availability` got here.
