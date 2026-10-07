# Agent catalog

Every lesson folder, its start command and the files it ships besides `agent.py`, `__init__.py` and
`CASES.md`. The folder name links to the lesson. For what each one teaches, see the table in the
[README](../README.md#the-agents).

- **agent**: has an `agent.py` with a `root_agent`. Chat with `uv run adk run <folder>`, or pick it in
  `uv run adk web`.
- **lab**: a plain script with no agent. Run it with `uv run python`.

The start command is the usual entry point. Many lessons use extra flags, environment switches or helper
scripts in later cases; the `CASES.md` gives the exact commands.

| # | Folder | Kind | Start with | Other files |
|---|---|---|---|---|
| 01 | [`agent01_poet`](../agent01_poet/CASES.md) | agent | `uv run adk run agent01_poet` | - |
| 02 | [`agent02_toolcall`](../agent02_toolcall/CASES.md) | agent | `uv run adk run agent02_toolcall` | - |
| 03 | [`agent03_localmodel`](../agent03_localmodel/CASES.md) | agent | `uv run adk run agent03_localmodel` | - |
| 04 | [`agent04_localmodelwithtool`](../agent04_localmodelwithtool/CASES.md) | agent | `uv run adk run agent04_localmodelwithtool` | - |
| 05 | [`agent05_state`](../agent05_state/CASES.md) | agent | `uv run adk run agent05_state` | - |
| 06 | [`agent06_structured`](../agent06_structured/CASES.md) | agent | `uv run adk run agent06_structured` | - |
| 07 | [`agent07_multiagent`](../agent07_multiagent/CASES.md) | agent | `uv run adk run agent07_multiagent` | - |
| 08 | [`agent08_workflow`](../agent08_workflow/CASES.md) | agent | `uv run adk run agent08_workflow` | - |
| 09 | [`agent09_parallel`](../agent09_parallel/CASES.md) | agent | `uv run adk run agent09_parallel` | - |
| 10 | [`agent10_loop`](../agent10_loop/CASES.md) | agent | `uv run adk run agent10_loop` | - |
| 11 | [`agent11_guardrails`](../agent11_guardrails/CASES.md) | agent | `uv run adk run agent11_guardrails` | - |
| 12 | [`agent12_mcp`](../agent12_mcp/CASES.md) | agent | `uv run adk run agent12_mcp` | `library_server.py` |
| 13 | [`agent13_evals`](../agent13_evals/CASES.md) | agent | `uv run adk run agent13_evals` | `bookshop.evalset.json`, `test_config.json`, `weak_config.json` |
| 14 | [`agent14_agent_as_tool`](../agent14_agent_as_tool/CASES.md) | agent | `uv run adk run agent14_agent_as_tool` | - |
| 15 | [`agent15_confirmation`](../agent15_confirmation/CASES.md) | agent | `uv run adk run agent15_confirmation` | - |
| 16 | [`agent16_chunking`](../agent16_chunking/CASES.md) | lab | `uv run python agent16_chunking/chunking.py` | - |
| 17 | [`agent17_embeddings`](../agent17_embeddings/CASES.md) | lab | `uv run python agent17_embeddings/embeddings_lab.py` | - |
| 18 | [`agent18_cosine`](../agent18_cosine/CASES.md) | lab | `uv run python agent18_cosine/cosine_lab.py` | - |
| 19 | [`agent19_retrieval`](../agent19_retrieval/CASES.md) | lab | `uv run python agent19_retrieval/retrieval_lab.py` | - |
| 20 | [`agent20_rag`](../agent20_rag/CASES.md) | agent | `uv run adk run agent20_rag` | `rag.evalset.json`, `rag_config.json` |
| 21 | [`agent21_memory`](../agent21_memory/CASES.md) | agent | `uv run adk run agent21_memory` | `memory_service_demo.py` |
| 22 | [`agent22_code_execution`](../agent22_code_execution/CASES.md) | agent | `uv run adk run agent22_code_execution` | - |
| 23 | [`agent23_artifacts`](../agent23_artifacts/CASES.md) | agent | `uv run adk run agent23_artifacts` | - |
| 24 | [`agent24_planning`](../agent24_planning/CASES.md) | agent | `uv run adk run agent24_planning` | `evaluate.py`, `puzzles.py` |
| 25 | [`agent25_multiturn_evals`](../agent25_multiturn_evals/CASES.md) | agent | `uv run adk run agent25_multiturn_evals` | `lunch.evalset.json`, `multiturn_config.json`, `rubric_config.json` |
| 26 | [`agent26_observability`](../agent26_observability/CASES.md) | agent | `uv run adk run agent26_observability` | `spans.py` |
| 27 | [`agent27_a2a`](../agent27_a2a/CASES.md) | agent | `uv run adk run agent27_a2a` | `remote_server.py` |
| 28 | [`agent28_multimodal`](../agent28_multimodal/CASES.md) | agent | `uv run adk run agent28_multimodal` | `ask_with_image.py`, `images/`, `make_images.py` |
| 29 | [`agent29_dynamic_instructions`](../agent29_dynamic_instructions/CASES.md) | agent | `uv run adk run agent29_dynamic_instructions` | - |
| 30 | [`agent30_long_conversations`](../agent30_long_conversations/CASES.md) | agent | `uv run adk run agent30_long_conversations` | `long_chat.py` |
| 31 | [`agent31_prompt_injection`](../agent31_prompt_injection/CASES.md) | agent | `uv run adk run agent31_prompt_injection` | `attack_test.py`, `pages/` |
| 32 | [`agent32_openapi_tools`](../agent32_openapi_tools/CASES.md) | agent | `uv run adk run agent32_openapi_tools` | `todo_api.py`, `todo_openapi.json` |
| 33 | [`agent33_long_running`](../agent33_long_running/CASES.md) | agent | `uv run adk run agent33_long_running` | `resume_demo.py` |
| 34 | [`agent34_persistent_sessions`](../agent34_persistent_sessions/CASES.md) | agent | `uv run adk run agent34_persistent_sessions` | `chat.py` |
| 35 | [`agent35_hybrid_rerank`](../agent35_hybrid_rerank/CASES.md) | lab | `uv run python agent35_hybrid_rerank/rerank_lab.py` | - |
| 36 | [`agent36_rag_eval`](../agent36_rag_eval/CASES.md) | lab | `uv run python agent36_rag_eval/rag_eval.py` | - |
| 37 | [`agent37_fewshot_selection`](../agent37_fewshot_selection/CASES.md) | agent | `uv run adk run agent37_fewshot_selection` | `examples.py`, `fewshot_lab.py` |
| 38 | [`agent38_many_tools`](../agent38_many_tools/CASES.md) | agent | `uv run adk run agent38_many_tools` | `tool_choice_test.py`, `tools.py` |
| 39 | [`agent39_cost_speed`](../agent39_cost_speed/CASES.md) | lab | `uv run python agent39_cost_speed/cost_lab.py` | - |
| 40 | [`agent40_fallback_timeouts`](../agent40_fallback_timeouts/CASES.md) | agent | `uv run adk run agent40_fallback_timeouts` | - |
| 41 | [`agent41_tool_auth`](../agent41_tool_auth/CASES.md) | agent | `uv run adk run agent41_tool_auth` | `notes_api.py`, `notes_openapi.json` |
| 42 | [`agent42_supervisor_critic`](../agent42_supervisor_critic/CASES.md) | agent | `uv run adk run agent42_supervisor_critic` | - |
| 43 | [`agent43_streaming`](../agent43_streaming/CASES.md) | agent | `uv run adk run agent43_streaming` | `stream_demo.py` |
| 44 | [`agent44_serving`](../agent44_serving/CASES.md) | agent | `uv run adk run agent44_serving` | `Dockerfile`, `client.py` |
| 45 | [`agent45_data_analyst`](../agent45_data_analyst/CASES.md) | agent | `uv run adk run agent45_data_analyst` | `analyst_test.py`, `grades.csv`, `make_data.py`, `tools.py` |
| 46 | [`agent46_graph_workflow`](../agent46_graph_workflow/CASES.md) | agent | `uv run adk run agent46_graph_workflow` | `flow_test.py` |
| 47 | [`agent47_batch_processing`](../agent47_batch_processing/CASES.md) | agent | `uv run adk run agent47_batch_processing` | `batch.py`, `reviews.py` |
| 48 | [`agent48_permissions`](../agent48_permissions/CASES.md) | agent | `uv run adk run agent48_permissions` | `permission_test.py`, `rate_limit_demo.py` |
| 49 | [`agent49_distillation`](../agent49_distillation/CASES.md) | lab | `uv run python agent49_distillation/distill_lab.py` | `messages.py`, `teacher_labels.json` |
| 50 | [`agent50_capstone`](../agent50_capstone/CASES.md) | agent | `uv run adk run agent50_capstone` | `capstone_test.py`, `client.py`, `eval_config.json`, `library.evalset.json`, `notices.md` |

## Lessons that need a second terminal

Start the server first, from the project root, then run the agent or client in another terminal.

| Agent | Terminal 1 | Terminal 2 |
|---|---|---|
| 27 | `uv run uvicorn agent27_a2a.remote_server:a2a_app --port 8001` | `uv run adk run agent27_a2a` |
| 32 | `uv run uvicorn agent32_openapi_tools.todo_api:api --port 8002` | `uv run adk run agent32_openapi_tools` |
| 41 | `uv run uvicorn agent41_tool_auth.notes_api:api --port 8003` | `uv run adk run agent41_tool_auth` |
| 44 | `uv run adk api_server --port 8004 agent44_serving` | `uv run python agent44_serving/client.py` |
| 50 | `uv run adk api_server --port 8005 --session_service_uri sqlite+aiosqlite:///agent50_capstone/library.db agent50_capstone` | `uv run python agent50_capstone/client.py` |

Agent 12 also uses a separate program, an MCP server, but the agent starts it itself as a child process, so
one terminal is enough.

## Lessons with a measuring script

These scripts run the agent many times and count results, so a claim in the lesson can be checked.
See [Evals and tests](evals-and-testing.md).

| Agent | Script | What it counts |
|---|---|---|
| 24 | `evaluate.py` | Puzzles solved in each planner mode |
| 30 | `long_chat.py` | Prompt tokens per turn over a fixed 14-turn chat, and whether early facts are still remembered, when you keep everything, trim, or summarise |
| 31 | `attack_test.py` | How often hidden instructions win under each defence level |
| 38 | `tool_choice_test.py` | Whether the model's first tool call was the right one, for three ways of offering 20 tools |
| 45 | `analyst_test.py` | Answers about `grades.csv` checked against pandas, for each analysis mode |
| 46 | `flow_test.py` | Whether each of 12 inputs took the right branch of the graph |
| 47 | `batch.py` | Throughput, retries and resume over many items |
| 48 | `permission_test.py` | How often a student role manages to change or delete data |
| 50 | `capstone_test.py` | 11 end-to-end scenarios, checked against stored bookings and preferences |

## Shared data

| File | Used by |
|---|---|
| `data/handbook.md` | The RAG labs, agent 20 and the capstone |
| `agent31_prompt_injection/pages/` | Product pages, some with hidden instructions, for the injection lesson |
| `agent28_multimodal/images/` | Sample images. `make_images.py` regenerates them. |
| `agent45_data_analyst/grades.csv` | The table the data analyst queries. `make_data.py` regenerates it. |
| `agent49_distillation/teacher_labels.json` | Labels produced by the big model, saved so the lab can be repeated |
| `agent50_capstone/notices.md` | A community notice board written by the public. The capstone reads it as untrusted data. |
