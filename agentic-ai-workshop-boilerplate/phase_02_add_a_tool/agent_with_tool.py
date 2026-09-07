"""
PHASE 2 -- Adding a second tool.

Run it:
    python phase_02_add_a_tool/agent_with_tool.py

WHAT'S NEW VS PHASE 1
-----------------------
Phase 1 had exactly one tool, so the LLM never had to choose between
options. Here we add a SECOND tool. The agent loop code is IDENTICAL to
phase_01 -- nothing about the loop changes when you add tools. All that
changes is:

    1. Write a new function, decorate it with @tool, write a good docstring.
    2. Add it to the `tools` list below.

That's the entire pattern for giving your agent a new capability. Do this
in your own track project: write a plain Python function that returns mock
data (a string, a number, a dict), decorate it, add it to the list.

This file is intentionally almost a copy-paste of phase_01 -- that
repetition is the point. Once the loop is familiar, adding tools is the
easy part.
"""

import sys

# Windows terminals default to a legacy codepage (cp1252) that can't print
# a lot of Unicode the model might return in its answers (smart quotes,
# em dashes, narrow spaces, etc.) and will crash with UnicodeEncodeError
# the moment it tries. Force UTF-8 output so that never happens, on any OS.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

load_dotenv()


# -----------------------------------------------------------------------
# Tool 1 (same as phase_01)
# -----------------------------------------------------------------------
@tool
def get_word_count(text: str) -> int:
    """Count how many words are in a piece of text."""
    return len(text.split())


# -----------------------------------------------------------------------
# Tool 2 (new!) -- a mock "lookup" tool. In a real project this might hit
# a CSV, a database, or an API. Here it's just a Python dict, which is all
# you need for this workshop -- mocked data is the whole point.
# -----------------------------------------------------------------------
MOCK_STUDENT_RECORDS = {
    "kumar": {"program": "Robotics & AI", "year": 1},
    "anjali": {"program": "Cybersecurity", "year": 3},
    "priya": {"program": "MTech", "year": 1},
}


@tool
def lookup_student(name: str) -> str:
    """Look up a student's program and year by their first name (lowercase).
    Use this when the user asks about a specific student's program or year.
    If the name isn't found, say so clearly."""
    record = MOCK_STUDENT_RECORDS.get(name.lower())
    if record is None:
        return f"No record found for '{name}'."
    return f"{name.title()} is a Year {record['year']} student in {record['program']}."


# -----------------------------------------------------------------------
# Everything below is the SAME agent loop as phase_01. Compare the two
# files side by side if it helps -- the only real difference is the
# `tools` list has two entries instead of one.
# -----------------------------------------------------------------------
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
    max_tokens=512,  # keep well under Groq free-tier output-tokens-per-minute limits
)

tools = [get_word_count, lookup_student]  # <-- this is the whole "add a tool" pattern
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


def run_agent(user_input: str) -> str:
    messages = [HumanMessage(content=user_input)]

    print(f"\nThinking about: \"{user_input}\"")
    ai_message = llm_with_tools.invoke(messages)
    messages.append(ai_message)

    if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"Calling tool: {tool_name}({tool_args})")

            selected_tool = tools_by_name[tool_name]
            result = selected_tool.invoke(tool_args)
            print(f"   -> tool result: {result}")

            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

        final_message = llm_with_tools.invoke(messages)
        print(f"Final answer: {final_message.content}")
        return final_message.content

    print(f"Final answer: {ai_message.content}")
    return ai_message.content


if __name__ == "__main__":
    # Case 1: needs the NEW tool -- watch the agent pick it correctly even
    # though it now has two tools to choose from.
    run_agent("What program is kumar in, and what year?")

    # Case 2: needs the OLD tool instead (from phase_01) -- proves the same
    # agent can choose between multiple tools, not just use whichever is newest.
    run_agent("How many words are in: Groq makes inference very fast?")

    # Case 3: needs NO tool at all -- a plain math question the LLM can just
    # answer, so `ai_message.tool_calls` comes back empty on the first call.
    run_agent("What is 17 times 6?")
