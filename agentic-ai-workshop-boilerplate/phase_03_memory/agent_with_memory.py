"""
PHASE 3 -- Giving the agent memory.

Run it:
    python phase_03_memory/agent_with_memory.py

WHAT'S NEW VS PHASE 2
-----------------------
In phase_01 and phase_02, `run_agent()` built a brand-new `messages` list
every single call -- so the agent had total amnesia between calls. Ask it
"what's my name" right after telling it your name, and it wouldn't know,
because that first exchange was never in the list you gave it the second
time.

The fix is almost embarrassingly simple: keep ONE `messages` list ALIVE
across calls, instead of creating a fresh one each time. That list *is*
the agent's memory. There's no special "memory object" or database --
it's just... not throwing away the list.

Everything else (the tool-calling loop) is copy-pasted from phase_02
unchanged. Memory and tool-use are independent features that stack.
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


@tool
def get_word_count(text: str) -> int:
    """Count how many words are in a piece of text."""
    return len(text.split())


llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
)

tools = [get_word_count]
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}

# -----------------------------------------------------------------------
# THIS is the memory. It's a plain Python list, declared OUTSIDE the
# function, so it survives between calls to run_agent(). Every message
# the agent sends or receives gets appended here and never removed.
#
# (For a long-running production agent you'd eventually cap this list's
# length or summarize old messages to save tokens -- not a concern for a
# 60-minute workshop project, but worth knowing it's the next problem
# you'd hit.)
# -----------------------------------------------------------------------
conversation_history = []


def run_agent(user_input: str) -> str:
    print(f"\nYou said: \"{user_input}\"")

    # Append to the SHARED list instead of creating a new one.
    conversation_history.append(HumanMessage(content=user_input))

    ai_message = llm_with_tools.invoke(conversation_history)
    conversation_history.append(ai_message)

    if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            print(f"Calling tool: {tool_name}({tool_args})")

            selected_tool = tools_by_name[tool_name]
            result = selected_tool.invoke(tool_args)
            print(f"   -> tool result: {result}")

            conversation_history.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

        final_message = llm_with_tools.invoke(conversation_history)
        conversation_history.append(final_message)
        print(f"Agent: {final_message.content}")
        return final_message.content

    print(f"Agent: {ai_message.content}")
    return ai_message.content


def scripted_demo() -> None:
    """Proves memory works with a fixed, repeatable script -- no typing
    needed. This is what makes memory visible: the second question only
    makes sense if the first one was remembered."""
    run_agent("My name is Priya and I'm building the Cybersecurity track project.")
    run_agent("What track am I working on, and what's my name?")


def live_chat() -> None:
    """An optional REPL so you can test memory interactively instead of
    with the scripted demo. Type 'quit' to exit."""
    print("\n--- Live chat mode. Type 'quit' to exit. ---")
    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "quit":
            break
        run_agent(user_input)


if __name__ == "__main__":
    scripted_demo()

    # Uncomment the line below to keep chatting live and test memory
    # yourself (e.g. tell it something, then ask about it two turns later):
    # live_chat()
