"""Global model switch for the demo agents (agent07 onwards).

Set MODEL_PROVIDER in the project root .env to choose for every agent that uses
get_model(). Set <AGENT_NAME>_MODEL_PROVIDER to override a single agent.
"""
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

# Root .env holds the global choice. override=False keeps real environment
# variables in charge when they are set.
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)

# langchain-google-genai reads GOOGLE_GENAI_USE_VERTEXAI. A .env written for the ADK version of this
# tutorial says GOOGLE_GENAI_USE_ENTERPRISE instead, so accept that spelling too.
if os.environ.get("GOOGLE_GENAI_USE_ENTERPRISE") and not os.environ.get("GOOGLE_GENAI_USE_VERTEXAI"):
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

# The Google SDK logs a long notice about "automatic function calling" on every call. It does not apply here
# (LangChain runs the tools itself), so only real errors from that logger are shown.
logging.getLogger("google_genai.models").setLevel(logging.ERROR)

PROVIDERS = ("local", "gemini")


def provider_for(agent_name: str | None = None) -> str:
    """The provider an agent will use: AGENTNN_MODEL_PROVIDER if set, else MODEL_PROVIDER, else gemini."""
    specific = os.environ.get(f"{agent_name.upper()}_MODEL_PROVIDER") if agent_name else None
    return (specific or os.environ.get("MODEL_PROVIDER", "gemini")).lower()


def get_model(agent_name: str | None = None, provider: str | None = None, **settings) -> BaseChatModel:
    """Return the chat model for an agent, based on environment variables.

    Args:
        agent_name: e.g. "agent07". If AGENT07_MODEL_PROVIDER is set it wins
            over the global MODEL_PROVIDER.
        provider: "gemini" or "local" to ask for one provider directly, ignoring the environment
            (agent40 builds a primary and a backup model this way).
        settings: extra arguments for the chat model class, e.g. timeout=30 or model="gemini-2.5-pro".
    """
    provider = (provider or provider_for(agent_name)).lower()

    if provider == "gemini":
        # max_retries: when Google answers "429 RESOURCE_EXHAUSTED" (too many requests in a short time),
        # wait and try again instead of failing.
        settings.setdefault("model", os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"))
        settings.setdefault("max_retries", 6)
        return ChatGoogleGenerativeAI(**settings)

    if provider == "local":
        # LM Studio speaks the OpenAI protocol, so the OpenAI chat class works once it is pointed at
        # the local server. The model id must match LM Studio exactly.
        settings.setdefault("model", os.environ.get("LOCAL_MODEL_ID", "qwen3.5-9b"))
        settings.setdefault("base_url", os.environ.get("LOCAL_API_BASE", "http://127.0.0.1:1234/v1"))
        settings.setdefault("api_key", os.environ.get("LOCAL_API_KEY", "lm-studio"))
        return ChatOpenAI(**settings)

    raise ValueError(f"MODEL_PROVIDER must be one of {PROVIDERS}, got {provider!r}")
