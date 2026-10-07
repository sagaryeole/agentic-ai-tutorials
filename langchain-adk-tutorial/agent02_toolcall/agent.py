from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI

import common.models  # noqa: F401  (loads the root .env with the Google settings)

# A built-in tool is written as a small dict, not as a Python function: the search runs on Google's side.
google_search = {'google_search': {}}

agent = create_agent(
    model=ChatGoogleGenerativeAI(model='gemini-2.5-flash'),
    name='root_agent',
    system_prompt='Answer user questions to the best of your knowledge using tools and external information when needed.',
    tools=[google_search],
)
