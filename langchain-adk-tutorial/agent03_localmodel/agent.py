from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# LM Studio's OpenAI-compatible server (Developer tab -> Start Server)
LM_STUDIO_URL = "http://127.0.0.1:1234/v1"

agent = create_agent(
    # LM Studio speaks the OpenAI protocol, so the OpenAI chat class is used, pointed at the local server.
    # The model id must match the model identifier shown in LM Studio exactly.
    model=ChatOpenAI(
        model="qwen3.5-9b",
        base_url=LM_STUDIO_URL,
        api_key="lm-studio",
    ),
    name='root_agent',
    system_prompt='Answer user questions to the best of your knowledge.',
)
