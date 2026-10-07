from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# LM Studio's OpenAI-compatible server (Developer tab -> Start Server)
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"


def get_current_time(timezone: str = "UTC") -> dict:
    """Returns the current date and time in the given IANA timezone.

    Args:
        timezone: IANA timezone name, e.g. "UTC", "Europe/Stockholm", "Asia/Kolkata".

    Returns:
        A dict with the status and the current time, or an error message.
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        return {"status": "error", "message": f"Unknown timezone: {timezone}"}
    return {"status": "success", "timezone": timezone, "time": now.isoformat(timespec="seconds")}


agent = create_agent(
    # The model id must match the model identifier shown in LM Studio exactly.
    model=ChatOpenAI(
        model="qwen3.5-9b",
        base_url=LM_STUDIO_URL,
        api_key="lm-studio",
    ),
    name='root_agent',
    system_prompt='Answer user questions to the best of your knowledge. Use the get_current_time tool for any question about the current time or date.',
    tools=[get_current_time],
)
