# agent09_parallel: cases, easiest first

Run: `uv run chat agent09_parallel`, or `uv run langgraph dev` to see the branches and state in the browser.
Concept: a graph can run independent steps at the same time (fan out), and a later step merges the results (fan in).
Topic: an idea reviewer. Three reviewers (benefits, risks, cost) work at once, then a verdict writer combines them.
Model: set `MODEL_PROVIDER` in the root `.env`, or `AGENT09_MODEL_PROVIDER` for this agent only.

## How it executes
Control: FIXED STRUCTURE, set in code. The three reviewers run AT THE SAME TIME, then the
verdict runs once all three are finished.

```
 user idea
     │
     ▼
  read_idea  (no model: copies the idea into state["idea"])
     │  three edges leave this node
 ╔═══╪═══════════════════════════════════════════╗
 ║   ├─►┌───────────────────┐ ──► state["benefits"]
 ║   │  │ benefits_reviewer │                    ║
 ║   │  └───────────────────┘                    ║
 ║   ├─►┌───────────────────┐ ──► state["risks"] ║   all three start together,
 ║   │  │ risks_reviewer    │                    ║   the step ends when the
 ║   │  └───────────────────┘                    ║   slowest one finishes
 ║   └─►┌───────────────────┐ ──► state["cost"]  ║
 ║      │ cost_reviewer     │                    ║
 ║      └───────────────────┘                    ║
 ╚═════════════════════╤═════════════════════════╝
                       ▼  one edge FROM A LIST of nodes: waits for all three
 verdict_writer reads state["benefits"], state["risks"], state["cost"]
                       ▼
                 go / wait / no-go
```

## Case 1: one idea, three reviews, one verdict
> Start a vegetable garden at our school

Expect: replies from `benefits_reviewer`, `risks_reviewer`, `cost_reviewer` (in the order they finish), then `verdict_writer`.
Learn: one message fans out to three steps, and the results are merged in a final step.

## Case 2: the reviewers do not depend on each other
Look at the three reviews.
Expect: none refers to another's answer. Each only saw your idea.
Learn: run steps in parallel when the sub-tasks are independent. If one needs another's
output, put them one after the other (agent08).

## Case 3: each branch has its own state key
Send an idea, then type `/state`.
Expect: `idea`, `benefits`, `risks`, `cost` and `verdict` are all stored.
Learn: parallel branches must write to different keys. Try it: make `risks_reviewer` return `{"benefits": ...}` and run again.
LangGraph stops with an error saying that the key received several values in one step. It refuses to choose a winner
unless you give the key a merging rule. (`messages` has one, which is why all three may add a message.) Change it back afterwards.

## Case 4: fan out, then fan in
Open `agent.py` and read the last lines.
Expect: three `add_edge("read_idea", name)` lines, and one `add_edge(list(REVIEWERS), "verdict_writer")`.
Learn: several edges out of one node start the targets together. An edge from a list of nodes waits for all of them,
which is why `benefits`, `risks` and `cost` all exist when the verdict step starts.

## Case 5: does it actually run in parallel? (experiment)
Time one run. Then chain the reviewers instead (`read_idea` → benefits → risks → cost → verdict, as in agent08) and time it again.
Expect: with a hosted model like Gemini the chained version is slower. With a local
model the difference may be small, because LM Studio may process one request at a time.
Learn: parallel only saves time if the model backend can actually serve calls at once.
Change it back afterwards.

## Case 6: the same idea, different models
    AGENT09_MODEL_PROVIDER=local  uv run chat agent09_parallel
    AGENT09_MODEL_PROVIDER=gemini uv run chat agent09_parallel

Expect: similar bullets, but possibly different verdicts ("Go" from one model, "Wait" from the other).
Learn: the verdict is the model's judgement, not a fact. Different models weigh the same
inputs differently, so important decisions need a human or an evaluation.

## Case 7: a vague idea
> something cool

Expect: depends on the model. A careful model writes thin reviews ("lack of definition") and a "Wait" verdict. A weaker
model may invent details instead.
Learn: nothing in the workflow checks the input. Whether bad input is caught depends on
the model and the instructions, so add an explicit check if it matters.
