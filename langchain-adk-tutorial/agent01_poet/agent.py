from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

import common.models  # noqa: F401  (loads the root .env with the Google settings)

agent = create_agent(
    model=ChatGoogleGenerativeAI(model='gemini-2.5-flash'),
    name='root_agent',
    system_prompt='Answer user questions in a poetic way',
)
