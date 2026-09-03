"""
TRACK A -- Robotics: The Rescue Drone Triage Agent (REFERENCE SOLUTION)

Run it:
    python triage_agent.py

This is a working end state -- use it to demo from, or to compare against
if your own version in starter/ is stuck. Don't start here; start in
starter/triage_agent.py and only look at this if you're blocked or want
to check your approach after finishing.

Includes the stretch goal: a second agent drafts a short radio message
back to the field team for the single highest-priority report.
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


# =========================================================================
# Mock data -- a queue of drone damage reports radioed in after an
# earthquake. No real sensors: this is just a Python list of strings.
# =========================================================================
incoming_reports = [
    "Sector 4: structural collapse, movement detected under rubble",
    "Sector 1: minor cracks in two buildings, no injuries reported",
    "Sector 7: gas leak reported near a residential block, no visible fire yet",
    "Sector 2: bridge partially collapsed, no people visible in the area",
    "Sector 9: apartment block fully collapsed, multiple voices heard calling for help",
    "Sector 5: road blocked by debris, area otherwise looks stable",
]

# Where the agent logs its triage decisions. Each entry looks like:
#   {"report": "...", "priority_score": 8, "action": "send rescue team", "reasoning": "..."}
dispatch_list = []


@tool
def get_next_report() -> str:
    """Pop and return the next unprocessed drone report from the queue.
    Returns the exact string 'QUEUE_EMPTY' when there is nothing left --
    that's your signal to stop calling this tool and give your summary."""
    if not incoming_reports:
        return "QUEUE_EMPTY"
    return incoming_reports.pop(0)


@tool
def add_to_dispatch_list(report: str, priority_score: int, action: str, reasoning: str) -> str:
    """Log a triage decision for one report. `priority_score` is 1-10 (10 =
    most urgent, respond immediately). `action` must be exactly one of:
    'send rescue team', 'send drone for closer look', or 'deprioritize'.
    `reasoning` is a one-sentence explanation a human dispatcher could
    trust. Call this once per report, right after you decide on it."""
    dispatch_list.append({
        "report": report,
        "priority_score": priority_score,
        "action": action,
        "reasoning": reasoning,
    })
    return f"Logged: {report[:40]}...  ->  priority {priority_score} ({action})"


tools = [get_next_report, add_to_dispatch_list]

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


def run_agent_until_done(goal: str, max_iterations: int = 12) -> str:
    """Same loop as phase_04_multi_step_task/agent_task_chain.py -- loops
    the agent through tool-calling rounds until IT decides there's nothing
    left to do."""
    messages = [HumanMessage(content=goal)]

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
            print(f"  {tool_name}({tool_args})")

            selected_tool = tools_by_name[tool_name]
            result = selected_tool.invoke(tool_args)
            print(f"    -> {result}")

            messages.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

    print("Hit max_iterations without the agent declaring itself done.")
    return "Stopped early: max_iterations reached."


def print_dispatch_list() -> None:
    """Prints the current dispatch list, highest priority first."""
    ranked = sorted(dispatch_list, key=lambda entry: entry["priority_score"], reverse=True)
    print("\n" + "=" * 60)
    print("DISPATCH LIST (highest priority first)")
    print("=" * 60)
    for entry in ranked:
        print(f"[{entry['priority_score']:>2}] {entry['action']:<28} {entry['report']}")
        print(f"      reasoning: {entry['reasoning']}")


TRIAGE_GOAL = """
You are a disaster-response triage officer. You will repeatedly call
get_next_report to pull damage reports radioed in by drones flying over
an earthquake zone. Keep calling it until you receive the exact string
QUEUE_EMPTY -- that means the queue is empty and you should stop.

For EVERY report, before moving to the next one:
1. Plan silently: does this report mention trapped or injured people,
   structural collapse, fire, or gas leaks? Those raise urgency sharply.
   A report with no people mentioned and only minor damage is low urgency.
2. Assign a priority_score from 1-10 (10 = respond immediately, likely
   lives at risk right now; 1 = no immediate danger to people).
3. Pick exactly one action:
   - "send rescue team" -- clear signs of trapped/injured people
   - "send drone for closer look" -- damage is serious but unclear if
     anyone is affected, or details are ambiguous
   - "deprioritize" -- minor damage, no indication of people at risk
4. Write a one-sentence reasoning a human dispatcher could quickly trust.
5. Call add_to_dispatch_list with all four values.

When you get QUEUE_EMPTY, stop calling tools and reply with a short
plain-text summary of how many reports you triaged and the single most
urgent one.
"""


# =========================================================================
# STRETCH GOAL -- a second agent that drafts a radio message back to the
# field team for the single highest-priority item in the dispatch list.
# This is a separate, independent LLM call -- no tools needed, since its
# only job is to turn a decision that's already been made into a message.
# =========================================================================
def draft_radio_message() -> str:
    if not dispatch_list:
        return "No dispatch entries yet -- run the triage agent first."

    top = max(dispatch_list, key=lambda entry: entry["priority_score"])

    prompt = (
        "You are a calm, precise radio dispatcher. Write a SHORT radio message "
        "(2-3 sentences, plain language, no jargon) to send to a field rescue team "
        "based on this triage decision:\n\n"
        f"Report: {top['report']}\n"
        f"Priority: {top['priority_score']}/10\n"
        f"Action: {top['action']}\n"
        f"Reasoning: {top['reasoning']}\n"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


if __name__ == "__main__":
    run_agent_until_done(TRIAGE_GOAL)
    print_dispatch_list()

    print("\n" + "=" * 60)
    print("RADIO MESSAGE TO FIELD TEAM (stretch goal)")
    print("=" * 60)
    print(draft_radio_message())

    # -------------------------------------------------------------------
    # DEMO MOMENT -- add ONE new report live and re-run the agent on just
    # that report, then reprint the list. Watch it get triaged and
    # slotted into the ranking with visible reasoning.
    # -------------------------------------------------------------------
    print("\n\n>>> DEMO: a new report just came in live <<<")
    incoming_reports.append("Sector 3: fire spreading toward a school, no injuries yet")
    run_agent_until_done(TRIAGE_GOAL, max_iterations=3)
    print_dispatch_list()
