# agent06_structured: cases, easiest first

Run: `uv run chat agent06_structured` (LM Studio server must be running).
Concept: structured output. The result must match a schema (`ReviewAnalysis`), so other code can use it.
Topic: turning a free-text customer review into a record with `product`, `sentiment`, `topic`, `summary`, `needs_reply`.
Every reply should be a JSON object, with no prose around it.

## How it executes
Control: one model call whose result must match a schema. This agent has no tools. LangChain does allow
tools with `response_format`: they run first, and only the final answer is forced into the schema.

```
 free-text review
      │
      ▼
 ┌─────────────────────────────┐   schema (ReviewAnalysis) is sent with the request
 │ LLM, must fill in the schema│◄──────────────────────────────────────────────────
 └──────────────┬──────────────┘
                ▼
 ReviewAnalysis(product=..., sentiment=..., topic=..., summary=..., needs_reply=...)
                │
                └──► saved in the state as state["structured_response"]
```

## Case 1: a clear, unhappy review
> My new headphones arrived two weeks late and the box was crushed. Very disappointed.

Expect: product=headphones, sentiment=negative, topic=delivery, needs_reply=true.
Learn: the result matches the schema, not free text.

## Case 2: a clear, happy review
> Love this coffee maker, it makes great coffee every morning.

Expect: sentiment=positive, needs_reply=false.
Learn: the field descriptions in the schema guide the model, like tool docstrings do.

## Case 3: missing information
> It's okay I guess.

Expect: product="unknown", not an invented product name.
Learn: the instruction decides what happens when the input lacks data.

## Case 4: closed set of values
> The blender works great but it is way too expensive for what it is.

Expect: sentiment is one of the allowed words (likely "mixed"), and topic is one of the five allowed topics.
The model cannot return "pricey" or "expensive" as a topic.
Learn: `Literal` limits the model to a fixed list. It also forces a choice: this review talks about both
quality and price, but `topic` takes only one value (in testing the local model chose "price").

## Case 5: valid shape, wrong content
> Does this phone case fit the older model too?

Expect: valid output and `needs_reply=true` (a question). But `topic` may come out as "quality", when "other" fits better,
because no allowed topic really matches.
Learn: a schema guarantees the shape of the answer, not that it is correct. When no allowed value fits, the
model picks the closest one. A cheap fix is to give every `Literal` an honest "other" and say when to use it.

## Case 6: the result in the state
Send a review, then type `/state`.
Expect: the record appears under `structured_response`.
Learn: the validated object is saved in the state, so the code that called the agent (or the next step of a
workflow) can read `result["structured_response"]` as a Python object. This is how steps hand data to each other (agent08 onwards).

## Case 7: how the schema is enforced
Look at the lines the runner prints before the JSON.
Expect: on the local model, `[tool call] ReviewAnalysis({...})` followed by `[tool result] ReviewAnalysis: Returning structured response ...`.
Learn: LangChain has two ways to get a structured result and picks one for you. If the model has a native
"reply in this JSON schema" feature, it uses that. Otherwise it offers the schema to the model as a TOOL and reads
the arguments of the tool call, which is what you see here. Either way the result is validated against the class;
when validation fails, the error is sent back to the model so it can try again.
