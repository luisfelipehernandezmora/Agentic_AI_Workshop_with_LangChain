"""
PHASE 1 -- Your first agent.

Run it:
    python phase_01_first_agent/hello_agent.py

WHAT THIS FILE PROVES
----------------------
An "agent" is just an LLM that can be given TOOLS (regular Python functions)
and is allowed to decide, on its own, whether to call one before answering.
That decision loop is the whole trick. This file has exactly ONE tool, so
you can see the loop with nothing else going on:

    1. We send the LLM a question.
    2. The LLM decides: "I need to call a tool" OR "I can just answer."
    3. If it wants a tool, WE (the Python code) actually run that function --
       the LLM cannot execute code itself, it can only ASK for a function
       to be run, with what arguments.
    4. We hand the tool's result back to the LLM.
    5. The LLM now answers using that result.

This "LLM decides -> Python executes -> LLM continues" loop is the exact
same pattern every phase after this one uses, just with more tools, more
turns, or more agents. Learn it once here.

GROQ-SPECIFIC NOTES (things that differ from a generic LangChain tutorial)
---------------------------------------------------------------------------
- We import `ChatGroq` from the `langchain_groq` package (NOT `ChatOpenAI`
  from `langchain_openai`). Most online LangChain tutorials use OpenAI --
  the class name and import path are the main things that change.
- `ChatGroq` automatically reads the `GROQ_API_KEY` environment variable,
  same as how OpenAI's class reads `OPENAI_API_KEY`. You never type your
  key into code.
- The `model` name is Groq-specific (e.g. "qwen/qwen3.8-27b"), not
  an OpenAI model name like "gpt-4o". Not every model Groq hosts supports
  tool-calling -- if you swap models and tools stop being called, that's
  the first thing to check. See https://console.groq.com/docs/models
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

# Load GROQ_API_KEY (and GROQ_MODEL) from the .env file into the environment.
load_dotenv()


# -----------------------------------------------------------------------
# STEP 1: Define a tool.
#
# A tool is just a normal Python function with a `@tool` decorator on it.
# The docstring is NOT decoration -- the LLM literally reads it to decide
# WHEN to call this function and HOW to fill in its arguments. Write
# docstrings like you're explaining the function to someone who can only
# read the description, never the code.
# -----------------------------------------------------------------------
@tool
def get_word_count(text: str) -> int:
    """Count how many words are in a piece of text. Use this whenever the
    user asks how long something is, or how many words it contains."""
    return len(text.split())


# -----------------------------------------------------------------------
# STEP 2: Set up the LLM ("the intelligence layer") and tell it which
# tools it's allowed to ask for ("the agentic layer" starts here).
# -----------------------------------------------------------------------
llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,  # 0 = consistent/predictable answers, good for demos and debugging
)

tools = [get_word_count]
llm_with_tools = llm.bind_tools(tools)

# A lookup so we can find the actual Python function by the name the LLM
# gives back to us (the LLM only ever sends us a tool's *name*, as text).
tools_by_name = {t.name: t for t in tools}


def run_agent(user_input: str) -> str:
    """The agent loop. This function is the part worth re-reading slowly --
    every later phase is a variation on it."""

    # The conversation so far, as a list of messages. We start with just
    # the user's question.
    messages = [HumanMessage(content=user_input)]

    # STEP 3: Ask the LLM what it wants to do.
    print(f"\nThinking about: \"{user_input}\"")
    ai_message = llm_with_tools.invoke(messages)
    messages.append(ai_message)

    # STEP 4: Did the LLM ask to call a tool?
    # `ai_message.tool_calls` is empty if the LLM decided it can answer
    # directly with no tool. It's a non-empty list if it wants one (or
    # more) tools run first.
    if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"Calling tool: {tool_name}({tool_args})")

            # WE run the actual Python function here -- the LLM never
            # executes code itself, it only requests it.
            selected_tool = tools_by_name[tool_name]
            result = selected_tool.invoke(tool_args)
            print(f"   -> tool result: {result}")

            # Feed the tool's result back into the conversation so the
            # LLM can use it in its final answer.
            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

        # STEP 5: Ask the LLM again, now that it has the tool result.
        final_message = llm_with_tools.invoke(messages)
        print(f"Final answer: {final_message.content}")
        return final_message.content

    # No tool was needed -- the LLM's first response IS the final answer.
    print(f"Final answer: {ai_message.content}")
    return ai_message.content


if __name__ == "__main__":
    # Try changing this question! Ask something that clearly doesn't need
    # the tool (e.g. "What is the capital of France?") and watch the
    # agent skip the tool call entirely.
    run_agent("How many words are in the sentence: The quick brown fox jumps over the lazy dog?")
