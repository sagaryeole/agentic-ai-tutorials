# agent10_loop: cases, easiest first

Run: `uv run chat agent10_loop`, or `uv run langgraph dev` to see each round and the state in the browser.
Concept: a loop. A *conditional edge* sends the graph back to an earlier step until a stop condition is met.
Topic: a slogan writer (an LLM) and a checker (plain Python, no model). The checker enforces three rules and
either approves or sends feedback.
Rules: at most 6 words, contains a meaningful word (4+ letters) of the product you named, no exclamation mark.
Model: set `MODEL_PROVIDER` in the root `.env`, or `AGENT10_MODEL_PROVIDER` for this agent only.

## How it executes
Control: FIXED STRUCTURE with a REPEAT. The order inside a round is set in code. How many
rounds run depends on the checker, but never more than `MAX_ITERATIONS`.

```
 user: "a bicycle repair shop"
        │
        ▼    slogan_loop (MAX_ITERATIONS = 4)
 ╔═══════════════════════════════════════════════════════════════╗
 ║                                                               ║
 ║   ┌────────┐ state["draft"]  ┌─────────┐                      ║
 ║   │ writer ├────────────────►│ checker │  plain Python,       ║
 ║   │ (LLM)  │                 └────┬────┘  no model            ║
 ║   └───▲────┘                      │                          ║
 ║       │   rules NOT met           │ again_or_stop(state)     ║
 ║       │   state["feedback"]       │ (the conditional edge)   ║
 ║       └───────────────────────────┤                          ║
 ║                                   │ approved, or round 4     ║
 ╚═══════════════════════════════════╪══════════════════════════╝
                                     ▼
                                 loop ends (approved or not: the cap is a safety net)
```

## Case 1: the loop runs and improves the draft
> a bicycle repair shop

Expect: alternating `[writer]` and `[checker]` lines. The checker names the rule that failed
(for example "does not contain any of these words: bicycle, repair, shop"), and the next draft changes to fix it.
Learn: a loop is a draft, check and revise cycle. Each round uses the last round's output.

## Case 2: the code stops the loop
Watch the end of the run.
Expect: the checker replies "Approved" and the run ends right after, with no extra round.
Learn: the checker writes `approved` into the state. The function `again_or_stop` reads it and returns the name of the
next node: `"writer"` to go round again, or `END`. That function is the conditional edge; the feedback reaches the
writer the same way, through `state["feedback"]`.

## Case 3: the safety net
Set `MAX_WORDS = 0` in `agent.py`, so no slogan can pass, and run again.
Expect: four rounds of rejections, then the loop stops even though nothing was approved.
Learn: always cap a loop. Without `rounds >= MAX_ITERATIONS`, a rule that can never be met would keep looping, and every round
costs model calls. LangGraph has an emergency brake of its own (the recursion limit, which raises an error), but its default is about
10,000 steps, far too late to protect your bill. You can lower it per run with `config={"recursion_limit": 20}`.
Change it back afterwards.

## Case 4: feedback travels through state
Run a request, then type `/state`.
Expect: `draft` holds the writer's latest slogan, `feedback` the checker's last note, `rounds` the number of rounds used.
Learn: the writer's instruction is built from `state['feedback']` on every round. The `start` node sets it to an empty
string, which is why round 1 works before any feedback exists.

## Case 5: a step that is not an LLM
Look at `checker` in `agent.py`. It is an ordinary function with no model.
Learn: a node does not have to call a model. Use code for rules code can check
(word count, a required word). The ADK version of this tutorial went through two worse versions first, both with an LLM critic:
the model miscounted words ("5 words exceeds the limit of 6"), then it skipped a tool call in later rounds
and copied its earlier rejection, so the loop never ended on approval. A plain-Python checker has neither problem.

## Case 6: the same loop, different writers
    AGENT10_MODEL_PROVIDER=local  uv run chat agent10_loop
    AGENT10_MODEL_PROVIDER=gemini uv run chat agent10_loop

Expect: Gemini usually ends on an approved slogan within a round or two. The local model tends to need more rounds, may write
slogans that are too long, and sometimes swings between two rejected drafts until the cap stops it.
Learn: the checker makes the rules model-independent. Only the writing quality depends on the model.

## Case 7: what the rule does not catch
> a net worth calculator

Expect: a slogan like "Know Your True Worth." is approved, because it contains "worth", even though it does not
say "calculator".
Learn: the rule is "contains a word of the product", which is exactly what the code checks and no more. Rules
checked in code are exact but only as smart as you make them. Try tightening it, for example to require every word.

## Case 8: change the rules
Edit the checker, for example `MAX_WORDS = 3`, and run again.
Expect: more rounds, and a higher chance of hitting `MAX_ITERATIONS`.
Learn: the stop condition is part of the design. Stricter rules mean more loops and more cost.

## Case 9: compare the three workflow shapes
| Agent | Edges | Runs | Stops when |
|---|---|---|---|
| agent08 pipeline | `add_edge(a, b)` in a chain | steps one after another, once | the last step finishes |
| agent09 fan-out | several edges from one node, one edge from a list | steps at the same time, once | all steps finish |
| agent10 loop | `add_conditional_edges` pointing back | steps repeatedly | the edge function returns `END` |

Learn: choose by the shape of the work. A fixed chain, independent tasks, or "repeat until good".
It is all one tool: the same `StateGraph`, with different edges.
