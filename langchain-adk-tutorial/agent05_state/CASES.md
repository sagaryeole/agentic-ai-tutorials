# agent05_state: cases, easiest first

Run: `uv run chat agent05_state` (LM Studio server must be running).
Type each line as a separate message in the same conversation.
Concept: state. A dict that is stored with the conversation (LangGraph calls a conversation a *thread*).

## How it executes
Control: the LLM chooses the tool. The tools read and write the state, which lives
between messages in the same thread.

```
 "remember X"                         "what did I note?"
      │                                     │
      ▼                                     ▼
    LLM ──► save_note(X)                  LLM ──► list_notes()
                 │ returns Command(update=...)         │ reads runtime.state
                 ▼                                     ▼
        ┌────────────────────────────────────────────────┐
        │  STATE of this thread                          │
        │    messages = [...]     notes = ["X", ...]     │
        └────────────────────────────────────────────────┘
   new thread ──► state starts empty
```

## Case 1: one tool call
> Remember that my dentist appointment is on Friday at 14:00.

Expect: `save_note` is called, the agent confirms.
Learn: the model picks a tool and fills its argument from your sentence.

## Case 2: state survives a turn
> What did I ask you to remember?

Expect: `list_notes` is called, the answer mentions the dentist appointment on Friday at 14:00.
Learn: the answer comes from the state, not from the model's memory.

## Case 3: state accumulates
> Also note that I need to buy milk.
> List everything you have noted.

Expect: both notes returned, `total_notes` goes to 2.
Learn: state is read, changed and written back each call.

## Case 4: look at the state
Type `/state`.
Expect: `{"notes": ["...", "..."], "messages": 12}` (the number of messages will differ).
Learn: the conversation itself is state too: the key `messages`. `NotesState` in `agent.py` only adds the key `notes` next to it.

## Case 5: nothing saved, no invention
Type `/new` (or quit and start again) and ask:
> What did I ask you to remember?

Expect: "nothing saved", with no made-up notes.
Learn: a new thread starts with empty state. The instruction forbids invention,
so this also checks grounding.

## Case 6: how a tool writes state
Read `save_note` in `agent.py`.
Learn: a tool gets the state through the `runtime` parameter (LangChain fills it in; it is not part of the schema the model sees).
Reading is `runtime.state.get(...)`. Writing is different: the tool RETURNS `Command(update={...})`, and LangGraph applies the update
after the tool finishes. Changing `runtime.state` in place would be lost. Because the Command replaces the normal return value,
the tool also adds the `ToolMessage` the model will read.

## Case 7: where the state is kept
The state is stored by a *checkpointer*. `uv run chat` uses one that lives in memory, so quitting loses every thread.
Learn: a thread that survives a restart needs a checkpointer backed by a database (agent34). A new thread is not the same
as the same thread resumed.
