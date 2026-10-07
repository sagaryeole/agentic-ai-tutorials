from langchain.agents import AgentState
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from common.models import get_model  # global model switch, see common/models.py

MODEL_KEY = "agent10"  # lets AGENT10_MODEL_PROVIDER override the global choice
MAX_WORDS = 6
MAX_ITERATIONS = 4
model = get_model(MODEL_KEY)


class SloganState(AgentState):
    product: str
    draft: str
    feedback: str
    approved: bool
    rounds: int


def start(state: SloganState) -> dict:
    """The product is whatever the user typed. A new request starts a new set of rounds."""
    return {"product": state["messages"][-1].text, "feedback": "", "approved": False, "rounds": 0}


# On the first round the checker has not run yet, so the feedback is empty.
def writer(state: SloganState) -> dict:
    reply = model.invoke([
        SystemMessage(
            "You write a slogan for the product or idea the user names.\n"
            f"Reviewer feedback on your last draft (empty on the first round): {state['feedback']}\n\n"
            "If there is feedback, fix exactly what it says. Reply with the slogan only."
        ),
        ("user", state["product"]),
    ])
    draft = reply.text.strip()
    return {"draft": draft, "messages": [AIMessage(draft, name="writer")]}


# A plain-Python node. It has no model: it just checks the rules in code. A workflow step does not
# have to be an LLM. Rules that code can check (word count, a required word) should be checked by
# code, because models miscount, judge leniently, and sometimes skip a tool call.
def checker(state: SloganState) -> dict:
    slogan, product = state["draft"], state["product"]
    words = len(slogan.split())
    # Rule 2: contain at least one meaningful word (4+ letters) of the product.
    product_words = [w for w in product.lower().replace("-", " ").split() if len(w) >= 4]
    problems = []
    if words > MAX_WORDS:
        problems.append(f"too long: {words} words, the limit is {MAX_WORDS}")
    if "!" in slogan:
        problems.append("contains an exclamation mark")
    if not any(w in slogan.lower() for w in product_words):
        problems.append(f"does not contain any of these words: {', '.join(product_words)}")

    approved = not problems
    feedback = "Approved" if approved else "Rejected: " + "; ".join(problems)
    return {
        # the feedback is saved so the writer can read it next round
        "feedback": feedback,
        "approved": approved,
        "rounds": state["rounds"] + 1,
        "messages": [AIMessage(f"Approved ({words} words)" if approved else feedback, name="checker")],
    }


def again_or_stop(state: SloganState) -> str:
    """A CONDITIONAL edge: code looks at the state and names the next node. Stop when approved, or at the safety cap."""
    if state["approved"] or state["rounds"] >= MAX_ITERATIONS:
        return END
    return "writer"


# Runs writer, then checker, then writer again... until the checker approves
# or MAX_ITERATIONS is reached, whichever comes first.
loop = StateGraph(SloganState)
loop.add_node("start", start)
loop.add_node("writer", writer)
loop.add_node("checker", checker)
loop.add_edge(START, "start")
loop.add_edge("start", "writer")
loop.add_edge("writer", "checker")
loop.add_conditional_edges("checker", again_or_stop, ["writer", END])
agent = loop.compile(name="slogan_loop")
