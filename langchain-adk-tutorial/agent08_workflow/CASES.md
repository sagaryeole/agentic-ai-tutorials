# agent08_workflow: cases, easiest first

Run: `uv run chat agent08_workflow`, or `uv run langgraph dev` to see each step and the state in the browser.
Concept: a workflow written as a graph (LangGraph `StateGraph`) that runs its steps in a fixed order.
Topic: a study helper that explains a topic, writes a quiz, then gives the answers.
Model: set `MODEL_PROVIDER` in the root `.env`, or `AGENT08_MODEL_PROVIDER` for this agent only.

## How it executes
Control: FIXED ORDER, set in code. No LLM decides what runs next. The same path every time.

```
 user topic
     │
     ▼
 ┌───────────┐  state["explanation"]  ┌─────────────┐  state["quiz"]  ┌────────────┐
 │ explainer ├───────────────────────►│ quiz_writer ├────────────────►│ answer_key │
 └───────────┘                        └─────────────┘                 └─────┬──────┘
   step 1                                step 2                             │ step 3
                                                                            ▼
                                                              state["answers"] + reply
 Each step waits for the one before it.
```

The three words of LangGraph, all in `agent.py`:
- STATE: one dict shared by all steps (`StudyState`).
- NODE: a function that receives the state and returns the keys it changes.
- EDGE: "after this node, run that node".

## Case 1: the whole pipeline runs
> photosynthesis

Expect: three replies in order: `[explainer]`, `[quiz_writer]`, `[answer_key]`.
Learn: one user message triggers all the steps, with no extra prompting.

## Case 2: each step uses the previous step's output
Read the quiz questions and the answers against the explanation.
Expect: the questions only ask about things the explanation said, and the answers match it.
Learn: a node returns `{"explanation": ...}` and LangGraph saves it in the state. A later node reads
`state["explanation"]` and puts it into its own instruction with an f-string.

## Case 3: the order never changes
> the French Revolution
> how a bicycle stays upright

Expect: explainer, then quiz_writer, then answer_key, every time.
Learn: no model decides the order, unlike the coordinator in agent07.
A workflow gives predictable control. Use one when the steps are always the same.

## Case 4: look at the state
Send a topic, then type `/state`.
Expect: `explanation`, `quiz` and `answers` are stored.
Learn: this is how steps hand data to each other, the same state as in agent05 and agent06.

## Case 5: a vague or odd input
> stuff

Expect: the pipeline still runs all three steps and may produce a thin or invented explanation.
Learn: a workflow does not check the quality of its input. A wrong or empty early step
passes into every later step. Validation is something you add on purpose.

## Case 6: compare with agent07
Ask agent07 "what is photosynthesis and then quiz me". Compare with this pipeline.
Expect: agent07 may do part of the job in a different order, and a coordinator is not a pipeline.
Learn: use a coordinator (LLM decides) when the path varies. Use a workflow when it is fixed.

## Case 7: switch the model
    AGENT08_MODEL_PROVIDER=local  uv run chat agent08_workflow
    AGENT08_MODEL_PROVIDER=gemini uv run chat agent08_workflow

Expect: the same three steps. Gemini is usually faster and more careful about "use only the explanation".
Learn: the pipeline is independent of the model behind it.

## Case 8: what each step is shown
Read `run_step` in `agent.py`: a step gets its instruction and the user's topic, not the other steps' replies.
Learn: the first version of this port sent every step the whole conversation. On the local model the third step then
echoed its own instruction instead of answering. Passing each step exactly what it needs, through the state, fixed it.
A step here is one plain model call (`model.invoke`); a node can also be a whole agent made with `create_agent`, as in agent07.
