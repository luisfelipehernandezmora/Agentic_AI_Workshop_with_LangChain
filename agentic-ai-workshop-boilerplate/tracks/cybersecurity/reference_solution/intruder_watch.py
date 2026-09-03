"""
TRACK C -- Cybersecurity: Catch the Intruder (REFERENCE SOLUTION)

Run it:
    python intruder_watch.py

This is a working end state -- use it to demo from, or to compare against if your own version
in starter/ is stuck. Don't start here; start in starter/intruder_watch.py.

Includes the stretch goal: a short alert email drafted for the single highest-severity
incident found.
"""

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

load_dotenv()


# =========================================================================
# Mock data -- a stream of login attempts. No real network traffic: this
# is just a list of dicts.
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
    incidents.append({
        "incident_type": incident_type,
        "description": description,
        "severity": severity,
        "reasoning": reasoning,
    })
    return f"Flagged: {incident_type} ({severity}) -- {description[:40]}..."


tools = [get_login_stream, lookup_ip_location, flag_incident]

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


def run_agent_until_done(goal: str, max_iterations: int = 12) -> str:
    """Same loop as phase_04_multi_step_task/agent_task_chain.py."""
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


INVESTIGATION_GOAL = """
You are a security analyst reviewing login activity for suspicious behavior.

1. Call get_login_stream exactly once to see every login attempt recorded so far.
2. Look for three patterns:
   - BRUTE FORCE: several failed login attempts for the same username and/or
     IP address, clustered within a short time window (a couple of minutes or
     less), especially if followed by a sudden success.
   - IMPOSSIBLE TRAVEL: the same username has two SUCCESSFUL logins from
     different IP addresses close together in time. Use lookup_ip_location on
     both IPs to check whether real travel between those locations would be
     physically possible in that time window. If it isn't, flag it.
   - REPEATED FAILURES: a couple of failed logins for one username that don't
     look like a full brute-force burst, but are still worth a human glancing
     at.
3. For every pattern you find, call flag_incident with its type, a short
   description, a severity ('low', 'medium', or 'high'), and your reasoning.
   Do NOT flag a single normal failed-then-succeeded login for the same
   user and IP a few seconds apart -- that's just a typo, not an incident.
4. When you've reviewed everything and flagged what's worth flagging, stop
   calling tools and write a short plain-text incident report: how many
   incidents you found and the single most urgent one.
"""


# =========================================================================
# STRETCH GOAL -- draft a short alert email to the security team for the
# single highest-severity incident found. A separate, independent LLM
# call -- no tools needed, since its only job is to turn a decision
# that's already been made into a message.
# =========================================================================
def draft_alert_email() -> str:
    if not incidents:
        return "No incidents flagged yet -- run the investigation first."

    top = min(incidents, key=lambda entry: SEVERITY_ORDER.get(entry["severity"], 3))

    prompt = (
        "You are a security analyst. Write a SHORT alert email (3-4 sentences, "
        "plain language, no jargon) to the security team based on this flagged "
        "incident:\n\n"
        f"Type: {top['incident_type']}\n"
        f"Severity: {top['severity']}\n"
        f"Description: {top['description']}\n"
        f"Reasoning: {top['reasoning']}\n"
    )
    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


if __name__ == "__main__":
    run_agent_until_done(INVESTIGATION_GOAL)
    print_incident_report()

    print("\n" + "=" * 60)
    print("ALERT EMAIL TO SECURITY TEAM (stretch goal)")
    print("=" * 60)
    print(draft_alert_email())

    # -------------------------------------------------------------------
    # DEMO MOMENT -- slip an obvious brute-force sequence into the stream
    # live, then re-run the investigation and watch it get caught.
    # -------------------------------------------------------------------
    print("\n\n>>> DEMO: an obvious attack just showed up live <<<")
    login_stream.extend([
        {"timestamp": "2026-09-09 09:00:01", "ip": "10.0.0.99", "username": "admin", "success": False},
        {"timestamp": "2026-09-09 09:00:04", "ip": "10.0.0.99", "username": "admin", "success": False},
        {"timestamp": "2026-09-09 09:00:07", "ip": "10.0.0.99", "username": "admin", "success": False},
        {"timestamp": "2026-09-09 09:00:10", "ip": "10.0.0.99", "username": "admin", "success": False},
        {"timestamp": "2026-09-09 09:00:13", "ip": "10.0.0.99", "username": "admin", "success": False},
        {"timestamp": "2026-09-09 09:00:16", "ip": "10.0.0.99", "username": "admin", "success": True},
    ])
    # get_login_stream always returns the WHOLE history, not just what's
    # new (unlike the Robotics track's queue, which drains). So the agent
    # re-reviews everything from scratch here -- clear old incidents
    # first, or you'll see the same impossible-travel entry flagged
    # twice in the printed report.
    incidents.clear()
    run_agent_until_done(INVESTIGATION_GOAL, max_iterations=6)
    print_incident_report()
