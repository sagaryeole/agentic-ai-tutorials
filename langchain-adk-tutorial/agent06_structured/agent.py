from typing import Literal
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# LM Studio's OpenAI-compatible server (Developer tab -> Start Server)
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"


# The output contract. LangChain sends this schema to the model and the result must
# match it, so other code can use the result without parsing prose.
class ReviewAnalysis(BaseModel):
    product: str = Field(description="The product the review is about, e.g. 'headphones'. 'unknown' if not stated.")
    sentiment: Literal["positive", "neutral", "negative", "mixed"] = Field(
        description="mixed = clearly both good and bad points; neutral = no strong feeling either way."
    )
    topic: Literal["quality", "price", "delivery", "customer_service", "other"] = Field(
        description="The main thing the review talks about."
    )
    summary: str = Field(description="One sentence summarising the review.")
    needs_reply: bool = Field(description="True if the customer is unhappy or asks a question.")


agent = create_agent(
    model=ChatOpenAI(
        model="qwen3.5-9b",
        base_url=LM_STUDIO_URL,
        api_key="lm-studio",
    ),
    name="root_agent",
    system_prompt=(
        "You receive a customer review. Fill in the required fields. Use only what "
        "the review says; if the product is not mentioned, set product to 'unknown'. "
        "Do not add fields or commentary."
    ),
    # The final result must match ReviewAnalysis. This agent has no tools, but LangChain
    # allows tools together with response_format: tools run first, and only the
    # final answer is forced into the schema.
    # The validated object is stored in the state under "structured_response" (see CASES.md case 6).
    response_format=ReviewAnalysis,
)
