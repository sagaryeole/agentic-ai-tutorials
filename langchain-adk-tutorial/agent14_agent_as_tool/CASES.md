# agent14_agent_as_tool: cases, easiest first

Run: `uv run chat agent14_agent_as_tool`.
Concept: an agent used as a tool. One agent calls another agent like a function, and the caller keeps control of the conversation.
Topic: a greeting-card writer that calls a translator agent when you ask for another language.
Model: set `MODEL_PROVIDER` in the root `.env`, or `AGENT14_MODEL_PROVIDER` for this agent only.
The agent prints a `[calling the sub-agent] ...` line each time it calls the translator.

## How it executes
Control: the LLM decides whether to call the translator (like any tool). The card writer stays in charge
and writes the final answer.

```
 user: "Birthday message for Anna in Swedish"
        │
        ▼
 ┌─────────────┐  1. writes English message
 │ card_writer │
 │   (LLM)     │  2. tool call: translator(text, target_language="Swedish")
 └──┬───────▲──┘                    │
    │       │ 4. result comes       ▼
    │       │    back like any   ┌────────────┐
    │       └────────────────────┤ translator │  3. its own model call,
    │                            │   (LLM)    │     returns only the translation
    │                            └────────────┘
    ▼ 5. card_writer writes the final answer (English + Swedish + a note)
  reply

 Compare agent07 (hand-off):
   root_agent ──hand-off──► weather_agent ... the specialist now owns the conversation and the next turns
   card_writer ──call──► translator ........ the translator returns a result and the card writer carries on
```

## Case 1: the tool is called
> Write a birthday message for my friend Anna in Swedish.

Expect: a `[calling the sub-agent] translator({'text': ..., 'target_language': 'Swedish'})` line, then a reply with the English
message, the Swedish translation and a short note. The reply is written by `[card_writer]`.
Learn: another agent can be a tool. The translator ran its own model call, but the user only sees the card writer.

## Case 2: no tool needed
> Write a thank-you note for my teacher.

Expect: an English message and no translator call.
Learn: as with any tool, the model decides. The instruction says to translate only when a language is named.

## Case 3: the caller keeps control
In the same conversation:
> Now write a get-well message for my neighbour in French.

Expect: a second tool call with `target_language` French, and the reply is again from `[card_writer]`.
Learn: unlike agent07, no other agent took over the conversation. The caller delegates one job and continues.

## Case 4: the wrapper is ten lines
Read the `translator` function in `agent.py`.
Learn: there is no special "agent tool" class. A tool is a function, and this function's body happens to run another agent:
it builds the sub-agent's input, calls `translator_agent.ainvoke(...)`, and returns the text of the last message. Two consequences:
- The sub-agent starts with an EMPTY conversation on every call. It knows only what the wrapper passes in.
- You choose what goes in and what comes back. Here only the translation is returned, not the sub-agent's whole conversation.

## Case 5: a typed input matters
Look at `TranslationRequest` in `agent.py`. Try the vague alternative: replace the tool's two parameters by a single
free-text one (`async def translator(request: str)`, without `args_schema`) and pass that string to the sub-agent.
Expect: the `[calling the sub-agent]` line now shows one string. A small model may forget to put the language in it
(`translator({'request': 'Happy Birthday, Anna! ...'})`), and then the translator just returns English.
Learn: named arguments (`text`, `target_language`) turn one vague string into a contract, like a
function signature, and the field descriptions tell the model what each one is for. Put it back afterwards.

## Case 6: the model skipping the tool
The problem to look for shows up on the SECOND request in the same conversation. Try on the local model:
> Write a thank-you note for my teacher.
> Now translate it into Swedish.

Expect: usually a translator call. Sometimes the model translates by itself, or only repeats the English message.
Cause: after one reply that already contains a translation, a small model copies that pattern instead of calling the tool again.
The instruction in `agent.py` is written against this: it has two steps, "Step 1, tool: ... call the translator BEFORE you
answer ... an earlier translation does not count", then "Step 2, answer". In the ADK version of this tutorial a one-sentence
instruction ("if a language is named, call the tool") made the local model skip the tool on follow-ups almost every time,
and the two-step version fixed nearly all of them.
Learn: a small model follows an instruction that puts the tool call first and says it must be repeated every
time much better than one that only says when to use the tool. It is still a request, not a guarantee: if you must
guarantee a translation, call the translator from code.

## Case 7: hand-off or tool?
| | Hand-off (agent07) | Agent as a tool (agent14) |
|---|---|---|
| Who talks to the user next | the specialist | the original agent |
| Result goes | straight to the user | back to the caller first |
| What the specialist sees | the conversation | only what the wrapper passes in |
| Good for | handing the whole conversation over | getting one piece of work done, then combining it |
| Cost | one agent per turn | caller + callee model calls on every use |

Learn: use a tool when the caller must combine, check, or reformat the result. Use a hand-off when the specialist
should take the conversation.
