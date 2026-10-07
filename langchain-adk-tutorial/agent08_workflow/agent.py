from langchain.agents import AgentState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from common.models import get_model  # global model switch, see common/models.py

MODEL_KEY = "agent08"  # lets AGENT08_MODEL_PROVIDER override the global choice
model = get_model(MODEL_KEY)


# The state of the pipeline: the conversation, plus one key per step where that step leaves its result.
class StudyState(AgentState):
    explanation: str
    quiz: str
    answers: str


def run_step(name: str, instruction: str, state: StudyState) -> AIMessage:
    """One model call for one step: the step's instruction, then the user's topic (the latest user message).
    A step does not see the other steps' replies in the conversation. What it needs from them is put into its instruction."""
    topic = next(m for m in reversed(state["messages"]) if isinstance(m, HumanMessage))
    reply = model.invoke([SystemMessage(instruction), topic])
    return AIMessage(reply.text.strip(), name=name)


# A NODE is a function: it receives the state and returns the keys it wants to change.
# Step 1: explain the topic. The reply is saved in the state under "explanation" so the next step can read it.
def explainer(state: StudyState) -> dict:
    reply = run_step("explainer", (
        "The user gives you a study topic. Explain it in 4-5 short sentences "
        "for a beginner. No headings, no quiz."
    ), state)
    return {"explanation": reply.text, "messages": [reply]}


# Step 2: the instruction is built from the value saved by step 1.
def quiz_writer(state: StudyState) -> dict:
    reply = run_step("quiz_writer", (
        "Write exactly 3 short quiz questions based only on this explanation:\n\n"
        f"{state['explanation']}\n\n"
        "Output a numbered list of questions only. No answers."
    ), state)
    return {"quiz": reply.text, "messages": [reply]}


# Step 3: reads both earlier results.
def answer_key(state: StudyState) -> dict:
    reply = run_step("answer_key", (
        f"Explanation:\n{state['explanation']}\n\n"
        f"Quiz:\n{state['quiz']}\n\n"
        "Give a one-sentence answer for each numbered question. "
        "Use only the explanation above."
    ), state)
    return {"answers": reply.text, "messages": [reply]}


# The EDGES fix the order: the graph runs its nodes in this order, every time.
# No LLM decides the order, unlike the coordinator in agent07.
pipeline = StateGraph(StudyState)
pipeline.add_node("explainer", explainer)
pipeline.add_node("quiz_writer", quiz_writer)
pipeline.add_node("answer_key", answer_key)
pipeline.add_edge(START, "explainer")
pipeline.add_edge("explainer", "quiz_writer")
pipeline.add_edge("quiz_writer", "answer_key")
pipeline.add_edge("answer_key", END)
agent = pipeline.compile(name="study_pipeline")
