# Shared code reference

The `common` package is installed into the virtual environment by `uv sync`, so these imports work from any
folder. Importing `common.models` loads the root `.env` without overriding variables that are already set;
the other modules import it. The variables are described in [Configuration](configuration.md).

## `common.models`

### `get_model(agent_name=None, provider=None, **settings) -> BaseChatModel`

Returns the chat model to pass to `create_agent(model=...)` or to call directly.

| Argument | Meaning |
|---|---|
| `agent_name` | For example `"agent07"`. If `AGENT07_MODEL_PROVIDER` is set, it wins over `MODEL_PROVIDER`. |
| `provider` | `"gemini"` or `"local"` to ask for one provider and ignore the environment |
| `**settings` | Extra arguments for the chat model class, for example `timeout=30`, `temperature=0` or `model="gemini-2.5-pro"` |

Returns a `ChatGoogleGenerativeAI` with `max_retries=6` (so a `429 RESOURCE_EXHAUSTED` is retried), or a
`ChatOpenAI` pointed at the local server. Raises `ValueError` for any other provider name.

```python
from langchain.agents import create_agent
from common.models import get_model

MODEL_KEY = "agent15"

agent = create_agent(
    model=get_model(MODEL_KEY),
    name="root_agent",
    system_prompt="Answer briefly.",
)
```

### `provider_for(agent_name=None) -> str`

The provider an agent will use: `AGENTNN_MODEL_PROVIDER` if set, else `MODEL_PROVIDER`, else `gemini`.

`PROVIDERS` is the tuple `("local", "gemini")`.

## `common.chat`

The module behind `uv run chat`. Its helpers are reused by the eval runner and can be reused by your own
scripts.

| Function | What it does |
|---|---|
| `await load_agent(folder, attribute="agent")` | Imports `<folder>/agent.py` from the current directory and returns its agent. A `make_agent()` function (sync or async) wins over a plain `agent` object. |
| `build_context(agent, user, settings)` | Fills the agent's `context_schema` (a dataclass) from a user id and a dict. Returns `None` for an agent without one. |
| `await run_turn(agent, payload, config, context, show_tokens=False, shown=None)` | Runs the agent on one user message, prints tool calls and replies, and handles pauses for human input |
| `await ask_human(interrupt_value)` | Asks on the terminal when an agent pauses, and returns the value to resume with |
| `main()` | The `chat` command |

```python
import asyncio
from langgraph.checkpoint.memory import InMemorySaver
from common.chat import load_agent

async def main():
    agent = await load_agent("agent07_multiagent")
    agent.checkpointer = agent.checkpointer or InMemorySaver()
    config = {"configurable": {"thread_id": "demo"}}
    result = await agent.ainvoke({"messages": [{"role": "user", "content": "What is the weather in Tokyo?"}]}, config)
    print(result["messages"][-1].text)

asyncio.run(main())
```

Run it from the project root, because `load_agent` imports the folder relative to the current directory.

## `common.evals`

The module behind `uv run evals`. See [Evals and tests](evals-and-testing.md) for the file formats.

| Function | What it does |
|---|---|
| `tool_trajectory(expected, actual) -> float` | `1.0` if the tool names and arguments match exactly and in order, else `0.0`. No model. |
| `response_overlap(reference, answer) -> float` | ROUGE-1 F-score, from 0 to 1: the share of words the two texts have in common. No model. It cannot tell "is" from "is not". |
| `await response_judge(question, reference, answer) -> (float, str)` | Asks the judge model whether the answer agrees with the reference. Returns `1.0` or `0.0` and a one-sentence reason. |
| `await run_case(agent, case, criteria, context) -> dict` | Plays one conversation in a new thread and scores every turn |
| `main()` | The `evals` command |

## `common.llm`

For code that needs "prompt in, text out" many times and has no use for an agent, tools or a session.

### `ask(prompt, system=None, model=None, max_tokens=None, temperature=0.0, provider_name=None) -> Reply`

| Argument | Meaning |
|---|---|
| `prompt` | The user message |
| `system` | The system instruction. When omitted, `DEFAULT_SYSTEM` ("You are a helpful assistant.") is sent, because the local model answered open questions oddly with no system instruction at all. |
| `model` | A model name that replaces `GEMINI_MODEL` or `LOCAL_MODEL_ID` for this call |
| `max_tokens` | A cap on the reply length |
| `temperature` | `0` means as repeatable as possible |
| `provider_name` | `"gemini"` or `"local"`. Default: `MODEL_PROVIDER`. Per-agent overrides do not apply. |

### `Reply`

| Field | Meaning |
|---|---|
| `text` | The reply, stripped |
| `prompt_tokens` | Tokens sent |
| `output_tokens` | Tokens produced, including Gemini's hidden "thinking" tokens, which are billed like output |
| `seconds` | Wall-clock time of the call |
| `cached_tokens` | Prompt tokens served from the provider's cache |

`to_reply(message, seconds)` builds a `Reply` from any LangChain `AIMessage`.

```python
from common.llm import ask

reply = ask("What is 2 + 2?")
print(reply.text, reply.prompt_tokens, reply.output_tokens, round(reply.seconds, 2))
```

## `common.embeddings`

### `embed_texts(texts, kind="document") -> numpy.ndarray`

Returns one vector per text as a 2D array (rows are texts). An empty list returns an empty array.

| Argument | Meaning |
|---|---|
| `texts` | The strings to embed |
| `kind` | `"document"` for text you search in, `"query"` for the question you search with. Gemini embeddings are tuned differently for the two; local models ignore it. |

Results are cached in memory for the life of the process, keyed by provider, model, kind and text.

### `embedding_provider() -> str`

The value of `EMBEDDING_PROVIDER`, lower-cased. Default `gemini`.

## `common.rag`

This module is identical to the ADK tutorial's copy.

### Loading and chunking

| Function | Returns |
|---|---|
| `load_handbook()` | The text of `data/handbook.md` |
| `fixed_size(text, size=300, overlap=60)` | Chunks of `size` characters, each sharing `overlap` characters with the one before |
| `sections(text)` | One chunk per `## ` heading, heading included |
| `paragraphs(text)` | One chunk per paragraph, headings removed |
| `paragraphs_with_heading(text)` | One chunk per paragraph, prefixed with its section title |

`CHUNKERS` maps a display name to each of the four functions.

### Keyword helpers

| Function | Returns |
|---|---|
| `tokens(text)` | The set of lower-case words, with codes like `lb-204` kept whole and stop words dropped |
| `keyword_overlap(query, chunk)` | The share of the query's words that appear in the chunk, from 0 to 1 |

### `Index(chunks)`

Embeds the chunks once and keeps them with their vectors.

`Index.search(query, k=3, min_score=0.0, keyword_weight=0.0) -> list[Hit]` returns up to `k` hits, best
first, dropping any whose final score is below `min_score`:

    final score = cosine + keyword_weight * keyword_overlap

`Hit` has `text`, `score` (the final score), `cosine` and `keyword`.

### Keyword search, fusion and reranking

| Name | What it does |
|---|---|
| `bm25_words(text)` | Like `tokens`, but a list, so repeats count |
| `BM25(chunks, k1=1.5, b=0.75)` | Classic keyword search. `.scores(query)` returns one score per chunk, in chunk order. |
| `ranking(scores)` | Chunk numbers, best score first. Ties keep the original order. |
| `reciprocal_rank_fusion(rankings, k=60)` | Merges several rankings using positions only, so cosine and BM25 can be combined with no weight to tune |
| `llm_rerank(query, chunks)` | Asks a model to score each chunk from 0 to 10 and returns positions best first |

`tests/test_rag.py` covers this module with a fake embedding function, so it runs without a model.
