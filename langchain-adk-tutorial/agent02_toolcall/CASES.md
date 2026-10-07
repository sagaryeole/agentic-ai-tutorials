# agent02_toolcall: cases, easiest first

Run: `uv run chat agent02_toolcall` (needs Vertex AI / GCP login, see README).
Concept: a built-in tool (`google_search`) the model can choose to call.

## How it executes
Control: the LLM decides, per message, whether to call the tool.

```
 user message
      │
      ▼
 ┌──────────┐   needs no tool   ┌──────────────┐
 │   LLM    ├──────────────────►│ final answer │
 └────┬─────┘                   └──────────────┘
      │ needs fresh info                ▲
      ▼                                 │
 google_search ──► results ──► LLM ─────┘
 (runs on Google's side)      (may search again)
```

## Case 1: no tool needed
> What does HTTP status 404 mean?

Expect: a direct answer, no `[google_search]` line.
Learn: the model decides whether to use a tool. You don't hardcode it.

## Case 2: tool needed for fresh information
> What is the latest stable version of Python?

Expect: a `[google_search] [...]` line with the search the model made, then an answer based on it.
Learn: tools give the model facts it cannot know from training.

## Case 3: compare with agent01
Ask agent01 and agent02 the same question from case 2.
Expect: agent01 answers from training data, possibly out of date. agent02 searches.
Learn: this is the difference between ungrounded and grounded answers.

## Case 4: where the search runs
Open `agent.py`. The tool is the dict `{'google_search': {}}`, not a Python function.
Expect: in the chat you see `[google_search]` but never a `[tool call]` / `[tool result]` pair (compare agent04).
Learn: a built-in tool runs inside the model provider. Your program sends one request and gets one grounded answer back, so
there is no agent loop on your side here. The loop with several model calls starts with your own tools, in agent04.

## Case 5: a limit of built-in tools
`google_search` is a Gemini feature. Copy this agent to a local model and it fails.
Learn: built-in tools depend on the model. This motivates agent03 and agent04.
