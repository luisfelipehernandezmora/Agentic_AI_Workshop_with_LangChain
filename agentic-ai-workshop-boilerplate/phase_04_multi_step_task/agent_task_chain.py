"""
PHASE 4 -- Chaining multiple steps toward a goal.

Run it:
    python phase_04_multi_step_task/agent_task_chain.py

WHAT'S NEW VS PHASE 1-3
--------------------------
Every phase so far did AT MOST one round of "call a tool, then answer."
Real tasks (and every track project today) need the agent to take SEVERAL
tool-calling steps in a row before it's actually done -- e.g. "go through
this whole queue of items, one at a time, and report on each."

The fix: instead of calling the LLM once and stopping, we loop, calling
the LLM again and again, feeding it each tool result, UNTIL THE LLM ITSELF
decides there's nothing left to do (it stops requesting tools and just
answers in plain text). We just cap it at `max_iterations` as a safety
net so a confused model can't loop forever.

This exact "loop until the model stops asking for tools" pattern is what
you'll use in your track project to process a whole list of drone reports
/ login attempts / a multi-agent conversation, not just one item.
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
# Mock data: a queue of items to inspect. In your track project this
# might be drone damage reports, login attempts, or study topics --
# anything you can represent as a Python list is fair game.
# -----------------------------------------------------------------------
sensor_queue = [
    "Sensor A: reading 22.1C, normal range",
    "Sensor B: reading 95.4C, DANGER threshold is 80C",
    "Sensor C: reading 21.8C, normal range",
    "Sensor D: no signal received",
]

# Where the agent logs what it found. A plain list, just like the queue.
findings = []


@tool
def get_next_sensor_reading() -> str:
    """Pop and return the next unprocessed sensor reading from the queue.
    Returns the exact string 'QUEUE_EMPTY' when there is nothing left --
    that is your signal to stop calling this tool and summarize instead."""
    if not sensor_queue:
        return "QUEUE_EMPTY"
    return sensor_queue.pop(0)


@tool
def record_finding(reading: str, verdict: str) -> str:
    """Record your verdict about one sensor reading. `verdict` should be a
    short judgement, e.g. 'normal', 'overheating - needs attention', or
    'no data - check connection'. Call this once per reading, right after
    you decide on it."""
    findings.append({"reading": reading, "verdict": verdict})
    return f"Logged: {verdict}"


llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
)

tools = [get_next_sensor_reading, record_finding]
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


def run_agent_until_done(goal: str, max_iterations: int = 10) -> str:
    """Loops the agent through as many tool-calling rounds as it needs,
    stopping when the LLM answers in plain text instead of requesting a
    tool -- i.e. when IT decides the goal is complete."""

    messages = [HumanMessage(content=goal)]

    for step in range(1, max_iterations + 1):
        print(f"\n--- Step {step} ---")
        ai_message = llm_with_tools.invoke(messages)
        messages.append(ai_message)

        # No tool calls this round => the model believes it's done.
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

    # Safety net: if we get here, the model never stopped asking for
    # tools within our budget. This should be rare with a clear goal
    # prompt, but it's why max_iterations exists.
    print("WARNING: Hit max_iterations without the agent declaring itself done.")
    return "Stopped early: max_iterations reached."


if __name__ == "__main__":
    run_agent_until_done(
        goal=(
            "There is a queue of sensor readings waiting to be inspected. "
            "Repeat the following until the queue is empty: get the next "
            "reading, decide if it is normal or a problem, and record your "
            "verdict. When you get QUEUE_EMPTY, stop and give me a one "
            "paragraph summary of everything you found."
        )
    )
    print("\nFinal findings log:")
    for f in findings:
        print(f"  - {f['reading']}  =>  {f['verdict']}")
