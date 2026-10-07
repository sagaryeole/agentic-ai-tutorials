"""Run an eval set against an agent and score the results.

    uv run evals agent13_evals agent13_evals/bookshop.evalset.json --config agent13_evals/test_config.json
    uv run evals agent13_evals agent13_evals/bookshop.evalset.json:book_details --config ... --details

An EVAL SET is a JSON file with cases. A case is a conversation: one or more turns, each with the user's message,
the tool calls you expect (optional) and a reference answer. A CONFIG file names the checks and the score each needs:

  tool_trajectory    1.0 if the agent called exactly the expected tools with exactly the expected arguments, in order; else 0.0.
                     Plain code, no model.
  response_judge     a second model (the JUDGE) reads the question, the reference and the agent's answer and says whether
                     they mean the same. 1.0 or 0.0. Costs one model call per turn.
  response_overlap   the share of words the answer and the reference have in common (ROUGE-1). Plain code, no model.

A case passes when, for every check, the average over its turns reaches the threshold. Each case runs in a new thread.
The judge model comes from JUDGE_PROVIDER (gemini or local; default gemini), so it can differ from the agent's model.

LangChain has no `eval` command of its own; hosted tools (LangSmith) and libraries (agentevals, openevals) offer
ready-made versions of these checks. This file is the same idea, small enough to read in one sitting.
"""
import argparse
import asyncio
import json
import os
import sys
import uuid
from pathlib import Path
from typing import Literal

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore
from pydantic import BaseModel, Field
from rouge_score import rouge_scorer

from common.chat import build_context, load_agent
from common.models import get_model

_rouge = rouge_scorer.RougeScorer(["rouge1"], use_stemmer=True)


def tool_trajectory(expected: list[dict], actual: list[dict]) -> float:
    """Exact match of names and arguments, in order."""
    same = [(e["name"], e.get("args", {})) for e in expected] == [(a["name"], a["args"]) for a in actual]
    return 1.0 if same else 0.0


def response_overlap(reference: str, answer: str) -> float:
    """ROUGE-1 F-score: how many words the two texts share, from 0 to 1. It cannot tell 'is' from 'is not'."""
    return _rouge.score(reference, answer)["rouge1"].fmeasure


class Verdict(BaseModel):
    reason: str = Field(description="One short sentence explaining the verdict.")
    verdict: Literal["valid", "invalid"]


JUDGE_INSTRUCTION = (
    "You grade the answer of an AI assistant. You get the user's question, a REFERENCE answer that is known to be correct, and the "
    "assistant's ANSWER. The answer is valid if it answers the question and agrees with the reference: wording, order, length and "
    "politeness do not matter, and details of the reference that the question did not ask for may be left out. "
    "It is invalid if it contradicts the reference, does not answer the question, or states facts that the reference shows to be wrong."
)


async def response_judge(question: str, reference: str, answer: str) -> tuple[float, str]:
    """Ask the judge model whether the answer means the same as the reference."""
    judge = get_model(provider=os.environ.get("JUDGE_PROVIDER", "gemini"), temperature=0).with_structured_output(Verdict)
    result = await judge.ainvoke([
        ("system", JUDGE_INSTRUCTION),
        ("user", f"Question: {question}\n\nREFERENCE: {reference}\n\nANSWER: {answer}"),
    ])
    return (1.0 if result.verdict == "valid" else 0.0), result.reason


async def run_case(agent, case: dict, criteria: dict, context) -> dict:
    """Play one conversation to the real agent, turn by turn, and score every turn."""
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    scores: dict[str, list[float]] = {name: [] for name in criteria}
    notes = []
    for number, turn in enumerate(case["turns"], start=1):
        before = len((await agent.aget_state(config)).values.get("messages", []))
        result = await agent.ainvoke({"messages": [{"role": "user", "content": turn["user"]}]}, config, context=context)
        new = result["messages"][before + 1:]   # everything the agent added after the user's message
        calls = [{"name": c["name"], "args": c["args"]} for m in new if isinstance(m, AIMessage) for c in m.tool_calls]
        answer = next((m.text for m in reversed(new) if isinstance(m, AIMessage) and m.text.strip()), "")
        notes.append(f"turn {number}: {turn['user']!r}\n      tools : {calls}\n      answer: {' '.join(answer.split())[:300]}")
        if "tool_trajectory" in criteria:
            scores["tool_trajectory"].append(tool_trajectory(turn.get("expected_tools", []), calls))
        if "response_overlap" in criteria:
            scores["response_overlap"].append(response_overlap(turn["reference"], answer))
        if "response_judge" in criteria:
            score, reason = await response_judge(turn["user"], turn["reference"], answer)
            scores["response_judge"].append(score)
            notes.append(f"      judge : {reason}")
    averages = {name: sum(values) / len(values) for name, values in scores.items()}
    return {"id": case["id"], "scores": averages, "passed": all(averages[n] >= criteria[n] for n in criteria), "notes": notes}


async def run(args) -> int:
    path, _, only = args.evalset.partition(":")
    eval_set = json.loads(Path(path).read_text())
    criteria = json.loads(Path(args.config).read_text())["criteria"]
    cases = [c for c in eval_set["cases"] if not only or c["id"] in only.split(",")]
    if not cases:
        print(f"No case named {only!r} in {path}")
        return 2

    agent = await load_agent(args.agent)
    agent.checkpointer = agent.checkpointer or InMemorySaver()
    agent.store = agent.store or InMemoryStore()
    context = build_context(agent, "student", dict(pair.split("=", 1) for pair in args.set))

    print(f"{eval_set['name']}: {len(cases)} case(s), checks: {criteria}\n")
    results = []
    for case in cases:   # one after another, so a local model is not asked to do several things at once
        result = await run_case(agent, case, criteria, context)
        results.append(result)
        shown = "  ".join(f"{name}={score:.2f}" for name, score in result["scores"].items())
        print(f"  {'PASSED' if result['passed'] else 'FAILED'}  {result['id']:<28} {shown}")
        if args.details or not result["passed"]:
            for note in result["notes"]:
                print(f"      {note}")
    passed = sum(r["passed"] for r in results)
    print(f"\nTests passed: {passed}\nTests failed: {len(results) - passed}")
    return 0 if passed == len(results) else 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Run an eval set against an agent of this tutorial.")
    parser.add_argument("agent", help="the agent folder, e.g. agent13_evals")
    parser.add_argument("evalset", help="the eval set file; add :case_id to run one case (or several, comma-separated)")
    parser.add_argument("--config", required=True, help="the file with the checks and their thresholds")
    parser.add_argument("--details", action="store_true", help="print the tool calls, the answer and the judge's reason for every case")
    parser.add_argument("--set", action="append", default=[], metavar="KEY=VALUE", help="a value for the agent's context")
    sys.exit(asyncio.run(run(parser.parse_args())))


if __name__ == "__main__":
    main()
