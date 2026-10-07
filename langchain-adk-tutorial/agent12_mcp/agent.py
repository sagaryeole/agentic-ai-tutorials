import sys
from pathlib import Path

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from common.models import get_model  # global model switch, see common/models.py

MODEL_KEY = "agent12"  # lets AGENT12_MODEL_PROVIDER override the global choice

SERVER_PATH = Path(__file__).parent / "library_server.py"

# The MCP client knows how to start the server as a child process and talk to it.
# None of the catalogue tools are written in this file.
library = MultiServerMCPClient({
    "library": {
        "transport": "stdio",
        "command": sys.executable,  # same Python (the uv venv) that runs the agent
        "args": [str(SERVER_PATH)],
    },
})

# Optional: expose only some of the server's tools to the model, e.g. {"list_books", "get_book"}.
TOOL_FILTER: set[str] | None = None


# Asking the server which tools it has means talking to another process, which is async. So this file has no
# ready-made `agent` object: it has a function that builds one. `uv run chat` and `langgraph dev` both call it.
async def make_agent():
    tools = await library.get_tools()   # starts the server, asks "which tools do you have?", wraps each one
    if TOOL_FILTER:
        tools = [t for t in tools if t.name in TOOL_FILTER]
    return create_agent(
        model=get_model(MODEL_KEY),
        name="root_agent",
        system_prompt=(
            "You are a librarian. Use the catalogue tools to answer questions about books. "
            "Answer only from tool results; if a book is not in the catalogue, say so. "
            "Say clearly whether a book is available."
        ),
        tools=tools,
    )
