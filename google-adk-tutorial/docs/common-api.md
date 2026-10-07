# Shared code reference

The `common` package is installed into the virtual environment by `uv sync`, so these imports work from any
folder. Every module loads the root `.env` on import and does not override variables that are already set.
The variables are described in [Configuration](configuration.md).

## `common.models`

### `get_model(agent_name=None, provider=None)`

Returns the model object to pass to `Agent(model=...)`.

| Argument | Meaning |
|---|---|
| `agent_name` | For example `"agent07"`. If `AGENT07_MODEL_PROVIDER` is set, it wins over `MODEL_PROVIDER`. |
| `provider` | `"gemini"` or `"local"` to ask for one provider and ignore the environment. Agent 40 builds a primary and a backup model this way. |

Returns a `google.adk.models.Gemini` with retry options for HTTP 429 and 503, or a `LiteLlm` pointed at the
local server. Raises `ValueError` for any other provider name.

```python
from google.adk.agents import Agent
from common.models import get_model

MODEL_KEY = "agent51"

root_agent = Agent(
    name="root_agent",
    model=get_model(MODEL_KEY),
    instruction="Answer briefly.",
)
```

`PROVIDERS` is the tuple `("local", "gemini")`.

## `common.llm`

For code that needs "prompt in, text out" many times and has no use for an agent, tools or a session.

### `ask(prompt, system=None, model=None, max_tokens=None, temperature=0.0, provider_name=None) -> Reply`

| Argument | Meaning |
|---|---|
| `prompt` | The user message |
| `system` | The system instruction. When omitted, `DEFAULT_SYSTEM` ("You are a helpful assistant.") is sent, because the local model answered open questions oddly with no system instruction at all. |
| `model` | A model name that replaces `GEMINI_MODEL` or `LOCAL_MODEL_ID` for this call. Used to compare models. |
| `max_tokens` | A cap on the reply length |
| `temperature` | `0` means as repeatable as possible |
| `provider_name` | `"gemini"` or `"local"`. Default: `MODEL_PROVIDER`. |

The Gemini path retries on 429 and 503. The local path posts to `{LOCAL_API_BASE}/chat/completions` with a
300 second timeout and raises on an HTTP error.

### `Reply`

| Field | Meaning |
|---|---|
| `text` | The reply, stripped |
| `prompt_tokens` | Tokens sent |
| `output_tokens` | Tokens produced. For Gemini this includes hidden "thinking" tokens, which are billed like output. |
| `seconds` | Wall-clock time of the call |
| `cached_tokens` | Prompt tokens Gemini served from its cache (0 for the local model) |

```python
from common.llm import ask

reply = ask("What is 2 + 2?")
print(reply.text, reply.prompt_tokens, reply.output_tokens, round(reply.seconds, 2))
```

### `provider(name=None) -> str`

The provider a call will use: `name` if given, otherwise `MODEL_PROVIDER`, lower-cased. It does not read
`AGENTNN_MODEL_PROVIDER`.

## `common.embeddings`

### `embed_texts(texts, kind="document") -> numpy.ndarray`

Returns one vector per text as a 2D array (rows are texts). An empty list returns an empty array.

| Argument | Meaning |
|---|---|
| `texts` | The strings to embed |
| `kind` | `"document"` for text you search in, `"query"` for the question you search with. Gemini embeddings are tuned differently for the two; local models ignore it. |

Results are cached in memory for the life of the process, keyed by provider, model, kind and text, so
repeating a text costs no new call. Gemini requests are sent in batches of 100.

### `embedding_provider() -> str`

The value of `EMBEDDING_PROVIDER`, lower-cased. Default `gemini`.

## `common.rag`

### Loading and chunking

| Function | Returns |
|---|---|
| `load_handbook()` | The text of `data/handbook.md` |
| `fixed_size(text, size=300, overlap=60)` | Chunks of `size` characters, each sharing `overlap` characters with the one before |
| `sections(text)` | One chunk per `## ` heading, heading included |
| `paragraphs(text)` | One chunk per paragraph, headings removed |
| `paragraphs_with_heading(text)` | One chunk per paragraph, prefixed with its section title: `"Loans: Books are lent for 21 days."` |

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

```python
from common.rag import Index, load_handbook, sections

index = Index(sections(load_handbook()))
for hit in index.search("How long can I keep a book?", k=3, min_score=0.45):
    print(round(hit.score, 2), hit.text.splitlines()[0])
```

### Keyword search, fusion and reranking (lab 35)

| Name | What it does |
|---|---|
| `bm25_words(text)` | Like `tokens`, but a list, so repeats count |
| `BM25(chunks, k1=1.5, b=0.75)` | Classic keyword search. `.scores(query)` returns one score per chunk, in chunk order. Rare words count for more than common ones. |
| `ranking(scores)` | Chunk numbers, best score first. Ties keep the original order. |
| `reciprocal_rank_fusion(rankings, k=60)` | Merges several rankings using positions only, so cosine and BM25 can be combined with no weight to tune |
| `llm_rerank(query, chunks)` | Asks a model to score each chunk from 0 to 10 and returns positions best first. Slow, so use it on the few candidates a cheap search already found. |

```python
from common.rag import BM25, Index, load_handbook, ranking, reciprocal_rank_fusion, sections

chunks = sections(load_handbook())
question = "Which form do I need to renew a loan?"

by_keyword = ranking(BM25(chunks).scores(question))
by_vector = [chunks.index(h.text) for h in Index(chunks).search(question, k=len(chunks))]
best = reciprocal_rank_fusion([by_vector, by_keyword])[:3]
```

`tests/test_rag.py` covers this module with a fake embedding function, so it runs without a model.
