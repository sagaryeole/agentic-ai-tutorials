from langchain.agents import AgentState
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from common.models import get_model  # global model switch, see common/models.py

MODEL_KEY = "agent09"  # lets AGENT09_MODEL_PROVIDER override the global choice
model = get_model(MODEL_KEY)


# Each reviewer writes to its OWN key. Parallel branches must not write the same key in the same step:
# LangGraph refuses that with an error (unless the key has a rule for merging, as `messages` has).
class ReviewState(AgentState):
    idea: str
    benefits: str
    risks: str
    cost: str
    verdict: str


def ask(name: str, instruction: str, text: str) -> AIMessage:
    reply = model.invoke([SystemMessage(instruction), ("user", text)])
    return AIMessage(reply.text, name=name)


def read_idea(state: ReviewState) -> dict:
    """No model here: copy the user's latest message into the state, so every reviewer reads the same text."""
    return {"idea": state["messages"][-1].text}


# Three independent reviewers. Each reads the same user idea.
def benefits_reviewer(state: ReviewState) -> dict:
    reply = ask("benefits_reviewer", "The user describes an idea. List its 3 biggest benefits as short bullet points. Bullets only.", state["idea"])
    return {"benefits": reply.text, "messages": [reply]}


def risks_reviewer(state: ReviewState) -> dict:
    reply = ask("risks_reviewer", "The user describes an idea. List its 3 biggest risks or downsides as short bullet points. Bullets only.", state["idea"])
    return {"risks": reply.text, "messages": [reply]}


def cost_reviewer(state: ReviewState) -> dict:
    reply = ask("cost_reviewer", (
        "The user describes an idea. In 2-3 sentences, say roughly what time, money and "
        "people it would take. Say clearly that it is a rough guess."
    ), state["idea"])
    return {"cost": reply.text, "messages": [reply]}


# Runs after the team, so all three state keys exist by now.
def verdict_writer(state: ReviewState) -> dict:
    reply = ask("verdict_writer", (
        "Three reviews of an idea are below.\n\n"
        f"Benefits:\n{state['benefits']}\n\n"
        f"Risks:\n{state['risks']}\n\n"
        f"Cost:\n{state['cost']}\n\n"
        "Write a verdict of 3-4 sentences: say go, wait, or no-go, and why. "
        "Use only the information above."
    ), state["idea"])
    return {"verdict": reply.text, "messages": [reply]}


REVIEWERS = {"benefits_reviewer": benefits_reviewer, "risks_reviewer": risks_reviewer, "cost_reviewer": cost_reviewer}

review = StateGraph(ReviewState)
review.add_node("read_idea", read_idea)
review.add_node("verdict_writer", verdict_writer)
review.add_edge(START, "read_idea")
for name, reviewer in REVIEWERS.items():
    review.add_node(name, reviewer)
    # Fan out: three edges leave read_idea, so the three reviewers start at the same time.
    review.add_edge("read_idea", name)
# Fan in: an edge from a LIST of nodes waits until all of them are done, then runs the merge step once.
review.add_edge(list(REVIEWERS), "verdict_writer")
review.add_edge("verdict_writer", END)
agent = review.compile(name="idea_review")
