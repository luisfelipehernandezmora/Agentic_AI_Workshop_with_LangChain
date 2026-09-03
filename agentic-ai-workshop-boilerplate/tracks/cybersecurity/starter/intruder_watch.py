"""
TRACK C -- Cybersecurity: Catch the Intruder

Run it:
    python intruder_watch.py

THE STORY
----------
Your agent watches a stream of login attempts (mocked: timestamp, IP address, username,
success/failure -- no real network traffic, no real logs). It reviews the whole stream and
flags suspicious patterns: brute-force attempts, impossible-travel logins (the same person
"logging in" from two far-apart places within minutes), and repeated failures. Then it drafts
a short incident report explaining its reasoning.

WHAT'S ALREADY DONE FOR YOU
------------------------------
- The mock login stream (`login_stream`) and a mock IP-to-location lookup (`IP_LOCATIONS`)
- `get_login_stream` and `lookup_ip_location` -- both fully working tools
- The full agent loop (`run_agent_until_done`) -- identical to phase_04_multi_step_task

WHAT YOU NEED TO BUILD (look for "TODO")
-------------------------------------------
1. `flag_incident` -- a few lines, append a dict to a list.
2. `INVESTIGATION_GOAL` -- the prompt that tells the agent what counts as suspicious. This is
   the real exercise. Use the cheat sheet's prompt template: goal, constraints (what each
   pattern actually looks like), plan-first.

If the agent misses an obvious attack, or flags something harmless (like one typo'd
password), that's a prompt problem -- go make INVESTIGATION_GOAL more specific.
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
# Mock data -- a stream of login attempts. No real network traffic: this
# is just a list of dicts. Add your own entries here too, or use the
# live-demo trick at the bottom.
# =========================================================================
login_stream = [
    {"timestamp": "2026-09-09 08:01:12", "ip": "203.0.113.5",  "username": "arun.k",  "success": True},
    {"timestamp": "2026-09-09 08:02:47", "ip": "198.51.100.9", "username": "priya.s", "success": True},
    {"timestamp": "2026-09-09 08:03:15", "ip": "203.0.113.5",  "username": "meera.j", "success": False},
    {"timestamp": "2026-09-09 08:03:52", "ip": "203.0.113.5",  "username": "meera.j", "success": True},
    {"timestamp": "2026-09-09 08:15:03", "ip": "192.0.2.44",   "username": "arun.k",  "success": True},
    {"timestamp": "2026-09-09 08:20:31", "ip": "198.51.100.9", "username": "priya.s", "success": False},
    {"timestamp": "2026-09-09 08:20:44", "ip": "198.51.100.9", "username": "priya.s", "success": False},
    {"timestamp": "2026-09-09 08:21:02", "ip": "198.51.100.9", "username": "priya.s", "success": True},
]

# Mock geolocation for each IP -- a real system would call a geolocation
# API here; we just use a dict.
IP_LOCATIONS = {
    "203.0.113.5": "Bengaluru, India",
    "198.51.100.9": "Chennai, India",
    "192.0.2.44": "Frankfurt, Germany",
}

# Where the agent logs incidents it finds. Each entry looks like:
#   {"incident_type": "brute force", "description": "...", "severity": "high", "reasoning": "..."}
incidents = []


@tool
def get_login_stream() -> str:
    """Return every login attempt recorded so far, one per line,
    formatted as 'timestamp | ip | username | SUCCESS or FAILURE'. Call
    this once at the start of your investigation to see everything."""
    lines = []
    for entry in login_stream:
        status = "SUCCESS" if entry["success"] else "FAILURE"
        lines.append(f"{entry['timestamp']} | {entry['ip']} | {entry['username']} | {status}")
    return "\n".join(lines)


@tool
def lookup_ip_location(ip: str) -> str:
    """Look up the approximate city/country an IP address connects from.
    Use this when you suspect impossible travel: the same username
    logging in successfully from two IPs close together in time."""
    return IP_LOCATIONS.get(ip, "Unknown location")


@tool
def flag_incident(incident_type: str, description: str, severity: str, reasoning: str) -> str:
    """Log one security incident you've found. `incident_type` must be
    exactly one of: 'brute force', 'impossible travel', 'repeated
    failures'. `severity` must be exactly one of: 'low', 'medium',
    'high'. `reasoning` is a one-sentence explanation a human security
    analyst could trust. Call this once per incident found."""
    # TODO: append a dict with keys "incident_type", "description",
    # "severity", "reasoning" to incidents (declared above). Same pattern
    # as add_to_dispatch_list in the Robotics track.
    ...

    return f"Flagged: {incident_type} ({severity}) -- {description[:40]}..."


tools = [get_login_stream, lookup_ip_location, flag_incident]

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


def run_agent_until_done(goal: str, max_iterations: int = 12) -> str:
    """Same loop as phase_04_multi_step_task/agent_task_chain.py -- loops
    the agent through tool-calling rounds until IT decides there's
    nothing left to do. You shouldn't need to change this function."""
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


SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def print_incident_report() -> None:
    """Prints all flagged incidents, most severe first."""
    ranked = sorted(incidents, key=lambda entry: SEVERITY_ORDER.get(entry["severity"], 3))
    print("\n" + "=" * 60)
    print("INCIDENT REPORT (most severe first)")
    print("=" * 60)
    for entry in ranked:
        print(f"[{entry['severity'].upper():<6}] {entry['incident_type']:<20} {entry['description']}")
        print(f"          reasoning: {entry['reasoning']}")


# =========================================================================
# TODO: write the goal prompt.
#
# Use the cheat sheet's prompt template: goal, constraints, plan-first.
# It must tell the agent to:
#   - call get_login_stream once to see every attempt recorded so far
#   - look for brute force (many failed attempts, same user/IP, clustered
#     in time), impossible travel (same user, two successful logins from
#     far-apart locations too close together in time -- use
#     lookup_ip_location to check), and repeated failures worth a glance
#   - call flag_incident for every genuine pattern found, but NOT for a
#     single normal failed-then-succeeded login (typos happen)
#   - when done, stop and give a short plain-text incident summary
# =========================================================================
INVESTIGATION_GOAL = """
TODO: replace this with your own goal prompt. See the instructions above
and the cheat sheet's prompt-engineering template.
"""


if __name__ == "__main__":
    run_agent_until_done(INVESTIGATION_GOAL)
    print_incident_report()

    # -------------------------------------------------------------------
    # DEMO MOMENT -- once your agent works above, try this: slip an
    # obvious brute-force sequence into the stream live, then re-run the
    # investigation and watch it get caught and explained.
    # -------------------------------------------------------------------
    # login_stream.extend([
    #     {"timestamp": "2026-09-09 09:00:01", "ip": "10.0.0.99", "username": "admin", "success": False},
    #     {"timestamp": "2026-09-09 09:00:04", "ip": "10.0.0.99", "username": "admin", "success": False},
    #     {"timestamp": "2026-09-09 09:00:07", "ip": "10.0.0.99", "username": "admin", "success": False},
    #     {"timestamp": "2026-09-09 09:00:10", "ip": "10.0.0.99", "username": "admin", "success": False},
    #     {"timestamp": "2026-09-09 09:00:13", "ip": "10.0.0.99", "username": "admin", "success": False},
    #     {"timestamp": "2026-09-09 09:00:16", "ip": "10.0.0.99", "username": "admin", "success": True},
    # ])
    # # get_login_stream always returns the WHOLE history (unlike the
    # # Robotics track's queue, which drains) -- clear old incidents first
    # # or you'll see the same thing flagged twice in the report.
    # incidents.clear()
    # run_agent_until_done(INVESTIGATION_GOAL, max_iterations=6)
    # print_incident_report()
