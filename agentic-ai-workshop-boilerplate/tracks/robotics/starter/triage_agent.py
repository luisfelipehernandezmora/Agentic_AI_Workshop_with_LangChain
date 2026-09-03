"""
TRACK A -- Robotics: The Rescue Drone Triage Agent

Run it:
    python triage_agent.py

THE STORY
----------
After an earthquake, drones fly over the disaster zone and radio back short damage reports
(mocked as plain text -- no real drones, no real sensors, just strings). Your agent reads each
report, decides how urgent it is, and builds a live ranked dispatch list so rescue teams know
where to go first.

WHAT'S ALREADY DONE FOR YOU
------------------------------
- The mock queue of drone reports (`incoming_reports`)
- `get_next_report` -- pops the next report off the queue, same pattern as phase_04
- The full agent loop (`run_agent_until_done`) -- identical to phase_04_multi_step_task,
  because this is the exact same "loop until the model stops asking for tools" pattern

WHAT YOU NEED TO BUILD (look for "TODO")
-------------------------------------------
1. `add_to_dispatch_list` -- a few lines, just append a dict to a list.
2. `TRIAGE_GOAL` -- the prompt that tells the agent HOW to triage. This is the real exercise
   today. See the cheat sheet's prompt template: state the goal, the constraints, and tell it
   to plan before acting.

If your agent's priorities look weird or it ignores an action option, that's almost always a
PROMPT problem, not a code problem -- go make TRIAGE_GOAL more specific before you touch the
Python.
"""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

load_dotenv()


# =========================================================================
# Mock data -- a queue of drone damage reports radioed in after an
# earthquake. No real sensors: this is just a Python list of strings.
# Add your own reports here too, or use the live-demo trick at the bottom.
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
    # TODO: append a dict with keys "report", "priority_score", "action",
    # "reasoning" to dispatch_list (it's declared above, just above this
    # tool). Four values, straight into a dict -- that's the whole task.
    ...

    return f"Logged: {report[:40]}...  ->  priority {priority_score} ({action})"


tools = [get_next_report, add_to_dispatch_list]

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


def run_agent_until_done(goal: str, max_iterations: int = 12) -> str:
    """Same loop as phase_04_multi_step_task/agent_task_chain.py -- loops
    the agent through tool-calling rounds until IT decides there's nothing
    left to do. You shouldn't need to change this function."""
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


# =========================================================================
# TODO: write the goal prompt.
#
# Use the cheat sheet's prompt template: goal, constraints, plan-first.
# It must tell the agent to:
#   - call get_next_report repeatedly until it gets QUEUE_EMPTY
#   - for each report, decide a priority_score (1-10) and pick one action:
#     "send rescue team" / "send drone for closer look" / "deprioritize"
#   - give a one-sentence reasoning a human dispatcher could trust
#   - call add_to_dispatch_list for every report before moving to the next
#   - when the queue is empty, stop and give a short plain-text summary
# =========================================================================
TRIAGE_GOAL = """
TODO: replace this with your own goal prompt. See the instructions above
and the cheat sheet's prompt-engineering template.
"""


if __name__ == "__main__":
    run_agent_until_done(TRIAGE_GOAL)
    print_dispatch_list()

    # -------------------------------------------------------------------
    # DEMO MOMENT -- once your agent works above, try this: add ONE new
    # report live and re-run the agent on just the queue (which now has
    # only your new report in it), then reprint the list. Watch your new
    # report get triaged and slotted into the ranking.
    # -------------------------------------------------------------------
    # incoming_reports.append("Sector 3: fire spreading toward a school, no injuries yet")
    # run_agent_until_done(TRIAGE_GOAL, max_iterations=3)
    # print_dispatch_list()
