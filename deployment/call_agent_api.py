# python/m5/homework/agent.py
"""M5.2 Homework: Deploy Your Own Agent.

THE IDEA
The lab deployed a fairly bare-bones agent (no tools, no persona, just
create_deep_agent(model=model)) and you only ever talked to it through
Studio's chat panel. This homework has two parts: first, deploy an agent
with your personal touch; second, talk to it the way any other client
would, straight over the Agent Server API this lesson covers, instead of
through Studio.

WHAT YOU FILL IN
  TODO 1: write your own @tool-decorated function on a topic of your
    choosing. A plain Python dict lookup is enough, no external API or
    key required.
  TODO 2: write a system_prompt that gives the agent a persona of your
    choosing and tells it to call your tool before answering.
  Then open call_agent_api.py in this same folder for TODO 3, which talks
  to this deployed agent over HTTP instead of through Studio.

RUN
  cd python/m5/homework
  uv run langgraph dev
Then chat with your agent in the Studio window that opens, or see
call_agent_api.py to talk to it over the API instead.
"""

from langchain_core.tools import tool

from deepagents import create_deep_agent
from models import model


# TODO 1: replace this with your own @tool-decorated function.
@tool
def lookup_fact(topic: str) -> str:
    """TODO 1: replace this with your own tool on a topic of your choosing."""
    home_number = {'peter' : 41 , 'john':57 , 'ryan' : 65}
    return str(home_number.get(topic, f"No home number on file for {topic}."))

# TODO 2: replace this with your own persona system prompt.
SYSTEM_PROMPT = """You are a polite homebook agent for a perticualar compony , whenever the user 
asks for the  homenumber with the name use only tool lookup_fact to answer , if you dont find the answer written null , convert the name to lowercase before calling the tool."""

# `langgraph.json` points at this module-level variable: "./agent.py:graph".
graph = create_deep_agent(model=model, tools=[lookup_fact], system_prompt=SYSTEM_PROMPT)
