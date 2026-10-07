from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_tool_call
from langchain.tools import tool
from common.models import get_model  # global model switch, see common/models.py

MODEL_KEY = "agent14"  # lets AGENT14_MODEL_PROVIDER override the global choice


@wrap_tool_call
async def show_tool_call(request, handler):
    """Prints every tool call so you can see when the translator is used. Then lets the call go ahead."""
    print(f"[calling the sub-agent] {request.tool_call['name']}({request.tool_call['args']})")
    return await handler(request)


# The translator's INPUT contract. Without this, an agent used as a tool would take one free-text string, and a
# small model may forget to put the target language in it. With args_schema, the tool declares two
# separate, named arguments, just like a normal function tool.
class TranslationRequest(BaseModel):
    text: str = Field(description="The text to translate.")
    target_language: str = Field(description="The language to translate into, e.g. 'Swedish'.")


# A specialist with one narrow job. It does not talk to the user: the card writer calls it like a function.
translator_agent = create_agent(
    name="translator",
    model=get_model(MODEL_KEY),
    system_prompt=(
        "You are a translator. The input has the fields text and target_language. "
        "Reply with ONLY the text translated into target_language, nothing else."
    ),
)


# An AGENT AS A TOOL is a normal tool whose body runs another agent: build its input, invoke it, return its last message.
# The sub-agent starts with an empty conversation every time. It knows only what is passed in here.
@tool(args_schema=TranslationRequest)
async def translator(text: str, target_language: str) -> str:
    """Translates a short text into a target language."""
    request = TranslationRequest(text=text, target_language=target_language)
    result = await translator_agent.ainvoke({"messages": [{"role": "user", "content": request.model_dump_json()}]})
    return result["messages"][-1].text


# The main agent keeps control of the conversation. It calls the translator as a TOOL, receives the
# result like any tool result, and then writes the final answer itself.
# Compare agent07: there the coordinator HANDED the conversation to a specialist and was out of the loop.
agent = create_agent(
    name="card_writer",
    model=get_model(MODEL_KEY),
    system_prompt=(
        "You write short greeting-card messages (one or two sentences). You cannot translate: only the translator tool can.\n"
        "Step 1, tool: if the user's CURRENT message asks for a language other than English (also in a follow-up such as "
        "'now in French' or 'translate it'), you MUST call the translator tool BEFORE you answer, with the English message "
        "as text and that language as target_language. Do this again in every later message that names a language: "
        "an earlier translation does not count, and writing a translation yourself is wrong.\n"
        "Step 2, answer: show the English message, the translated message returned by the tool, and one short friendly note. "
        "If no language is named, reply with the English message only and do not call any tool."
    ),
    tools=[translator],
    middleware=[show_tool_call],
)
