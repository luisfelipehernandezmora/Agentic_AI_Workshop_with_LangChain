"""
TEMPLATE -- copy this file to start ANY new agent project.

This is the same pattern as phase_00 through phase_04, stripped down to a
fill-in-the-blanks skeleton. Every section below is marked with a TODO.
Work through them top to bottom. If you get stuck, go re-read the phase
that matches what you're trying to add:

    - Need a new tool?              -> phase_02_add_a_tool
    - Need the agent to remember?    -> phase_03_memory
    - Need it to process a LIST of things, one at a time, until done?
                                      -> phase_04_multi_step_task

HOW TO USE THIS FILE
----------------------
1. Copy it into your own project folder and rename it.
2. Fill in TODO 1 (mock data), TODO 2 (tools), TODO 3 (goal prompt).
3. Run it. Read the printed steps. Adjust your tool docstrings if the
   agent picks the wrong tool or the wrong arguments -- the docstring IS
   the instruction the LLM is following, so vague docstrings cause vague
   behavior.
4. Add more tools / more mock data as your project grows. The loop at the
   bottom never needs to change.
"""

import sys

# Windows terminals default to a legacy codepage (cp1252) that can't print
# a lot of Unicode the model might return in its answers (smart quotes,
# em dashes, narrow spaces, etc.) and will crash with UnicodeEncodeError
# the moment it tries. Force UTF-8 output so that never happens, on any OS.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

load_dotenv()


# =========================================================================
# TODO 1: Your mock data.
#
# No real sensors/APIs/databases in this workshop -- everything is a
# Python list, dict, or string standing in for the real thing. Replace
# this example with data shaped like YOUR project (e.g. a list of drone
# reports, a list of login attempts, a list of study topics).
# =========================================================================
MOCK_DATA = [
    "example item 1",
    "example item 2",
    "example item 3",
]

# A place for your agent to write down its output as it works. Shape this
# however fits your project (list of dicts is usually easiest).
results = []


# =========================================================================
# TODO 2: Your tools.
#
# Rules of thumb for a good tool:
#   - One tool = one clear action (don't make a tool that does five things)
#   - The docstring is the ONLY thing the LLM knows about this function --
#     say exactly when to use it and what each argument means
#   - Return a short string or simple value, not a huge blob of data
#   - If a tool represents "getting the next thing from a queue," make it
#     return a clear sentinel (e.g. "QUEUE_EMPTY") when there's nothing
#     left, so the agent has an unambiguous stop signal (see phase_04).
# =========================================================================
@tool
def example_tool(some_argument: str) -> str:
    """TODO: describe exactly when the agent should call this, and what
    `some_argument` means. Be specific -- this docstring is the agent's
    only instructions for this tool."""
    # TODO: replace with real logic (can be as simple as a dict lookup
    # or a plain if/else over mock data -- no real APIs needed).
    return f"processed: {some_argument}"


# Add more @tool functions here as your project needs them.
# Then list every one of them below:
tools = [example_tool]


# =========================================================================
# Agent setup -- you normally don't need to change this part.
# =========================================================================
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}

# Optional: a system message sets the agent's role/personality/rules.
# Uncomment and edit if your track wants the agent to behave a certain
# way (e.g. "You are a triage officer. Always give a priority score.").
# SYSTEM_PROMPT = "TODO: describe the agent's role and rules here."


# =========================================================================
# The agent loop -- same shape as phase_04. Copy it as-is; you almost
# never need to edit this part, only the TODOs above it.
# =========================================================================
def run_agent_until_done(goal: str, max_iterations: int = 10) -> str:
    messages = []
    # If you uncommented SYSTEM_PROMPT above, include it like this:
    # messages.append(SystemMessage(content=SYSTEM_PROMPT))
    messages.append(HumanMessage(content=goal))

    for step in range(1, max_iterations + 1):
        print(f"\n--- Step {step} ---")
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)

        if not ai_message.tool_calls:
            print(f"Agent finished: {ai_message.content}")
            return ai_message.content

        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"{tool_name}({tool_args})")

            selected_tool = tools_by_name[tool_name]
            result = selected_tool.invoke(tool_args)
            print(f"   -> {result}")

            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

    print("WARNING: Hit max_iterations without the agent declaring itself done.")
    return "Stopped early: max_iterations reached."


# =========================================================================
# TODO 3: Your goal prompt.
#
# This is where "prompt engineering" actually happens. A good goal prompt
# usually states: (1) what the agent's overall job is, (2) any
# constraints/format it must follow, (3) a "plan first, then act"
# instruction so it doesn't rush. See the cheat sheet for the full
# template.
# =========================================================================
if __name__ == "__main__":
    run_agent_until_done(
        goal=(
            "TODO: describe the agent's overall goal here. Be specific "
            "about what it should do with each item, and what the final "
            "output should look like."
        )
    )

    print("\nFinal results:")
    for r in results:
        print(f"  - {r}")
