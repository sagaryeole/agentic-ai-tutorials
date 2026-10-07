import json
import re

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import after_model, before_model, wrap_tool_call
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from common.models import get_model  # global model switch, see common/models.py

MODEL_KEY = "agent11"  # lets AGENT11_MODEL_PROVIDER override the global choice

MENU = {"margherita": 9, "pepperoni": 11, "veggie": 10}  # price per pizza
MAX_PIZZAS = 10

# A card number is 13-16 digits, optionally split by spaces or dashes.
CARD_PATTERN = re.compile(r"\b(?:\d[ -]?){13,16}\b")
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_PATTERN = re.compile(r"\b\d{3}[-.\s]\d{4}\b")


def get_menu() -> dict:
    """Returns the pizzas on the menu with the price of each one in dollars."""
    return {"menu": MENU}


def place_order(item: str, quantity: int) -> dict:
    """Places an order for pizzas.

    Args:
        item: The pizza name from the menu, e.g. 'margherita'.
        quantity: How many pizzas to order.
    """
    price = MENU[item.lower()]
    return {
        "status": "confirmed",
        "order_id": "A123",
        "item": item.lower(),
        "quantity": quantity,
        "total_dollars": price * quantity,
        # Internal detail that should never reach customers:
        "internal_note": "Kitchen contact: kitchen@pizzaplace.example or 555-0142",
    }


class PizzaState(AgentState):
    blocked_count: int


# MIDDLEWARE is code that runs around the model and around the tools. Three hooks are used here.

# 1. BEFORE the model: runs before every model call. Returning messages together with jump_to="end" skips
#    the model call entirely and ends the turn. Returning None lets the request go through.
@before_model(can_jump_to=["end"])
def block_card_numbers(state: PizzaState, runtime) -> dict | None:
    last_user_text = next((m.text for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
    if CARD_PATTERN.search(last_user_text) or "cvv" in last_user_text.lower():
        print("[guardrail] model call BLOCKED: message looks like it contains card details")
        return {
            "blocked_count": state.get("blocked_count", 0) + 1,
            "messages": [AIMessage("Please don't share card details in this chat. You can pay when your order arrives. Tell me what you'd like to order.", name="root_agent")],
            "jump_to": "end",
        }
    return None


# 2. AROUND a tool: runs with the arguments the model chose. `handler(request)` runs the real tool. Returning a
#    ToolMessage without calling the handler replaces the tool result, and the real function is never called.
@wrap_tool_call
async def validate_order(request, handler):
    call = request.tool_call
    if call["name"] != "place_order":
        return await handler(request)

    def refuse(message: str) -> ToolMessage:
        return ToolMessage(json.dumps({"status": "error", "message": message}), tool_call_id=call["id"], name=call["name"])

    item, quantity = str(call["args"].get("item", "")).lower(), call["args"].get("quantity")
    if item not in MENU:
        print(f"[guardrail] tool call BLOCKED: '{item}' is not on the menu")
        return refuse(f"'{item}' is not on the menu. Available: {', '.join(MENU)}.")
    if not isinstance(quantity, int) or not 1 <= quantity <= MAX_PIZZAS:
        print(f"[guardrail] tool call BLOCKED: quantity {quantity} is outside 1-{MAX_PIZZAS}")
        return refuse(f"Quantity must be between 1 and {MAX_PIZZAS}. Larger orders need a phone call to the shop.")
    return await handler(request)


# 3. AFTER the model: runs on every model reply. Here it hides staff contact details.
#    Returning a message with the SAME id replaces the model's reply in the conversation.
@after_model
def hide_staff_contacts(state: PizzaState, runtime) -> dict | None:
    reply = state["messages"][-1]
    if not isinstance(reply, AIMessage) or reply.tool_calls:
        return None  # leave tool requests alone
    cleaned = PHONE_PATTERN.sub("[number removed]", EMAIL_PATTERN.sub("[email removed]", reply.text))
    if cleaned == reply.text:
        return None
    print("[guardrail] reply MODIFIED: staff contact details removed")
    return {"messages": [AIMessage(cleaned, id=reply.id, name=reply.name)]}


agent = create_agent(
    model=get_model(MODEL_KEY),
    name="root_agent",
    system_prompt=(
        "You take pizza orders. Use get_menu to show the menu and place_order to order. "
        "Always confirm the order id and total after ordering. If a tool result contains "
        "an internal note, you may pass on the kitchen contact if the customer asks for it."
    ),
    tools=[get_menu, place_order],
    state_schema=PizzaState,
    middleware=[block_card_numbers, validate_order, hide_staff_contacts],
)
