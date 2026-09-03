# Track A -- Robotics: The Rescue Drone Triage Agent

**The story:** After an earthquake, drones fly over the disaster zone and radio back short
damage reports (mocked as plain text strings -- no real drones, no real sensors). Your agent
reads each report, decides how urgent it is, and builds a live ranked dispatch list so rescue
teams know where to go first.

## What "done" looks like

- The agent processes every report in the mock queue.
- For each one it assigns a **priority score**, picks an **action** (send rescue team / send
  drone for closer look / deprioritize), and gives a one-sentence **reasoning**.
- You get a printed dispatch list, ranked highest priority first.

**Demo moment:** with your agent working, paste in ONE new report live (see the bottom of the
file) and watch it get triaged and slotted into the ranking with visible reasoning -- that's
the moment to show off at 3:45.

## Where to start

Open `starter/triage_agent.py`. It already has:

- The mock queue of drone reports
- A working `get_next_report` tool (same pattern as `phase_04_multi_step_task`)
- The full agent loop (copy-pasted from `phase_04` -- you already know how this works)

You need to fill in two `TODO`s:

1. `add_to_dispatch_list` -- a few lines, just append a dict to a list.
2. `TRIAGE_GOAL` -- the prompt that tells the agent HOW to triage. This is the real exercise.
   Use the prompt template from the cheat sheet: state the goal, the constraints (what counts
   as urgent, what the three actions mean), and tell it to plan before acting.

If your agent picks weird priorities or ignores an action option, that's almost always a
prompt problem, not a code problem -- go back and make `TRIAGE_GOAL` more specific.

## If you're stuck

Compare against `reference_solution/triage_agent.py` -- don't copy it before trying, but it's
there if you're out of time or well and truly blocked.

## Stretch goal

If your core loop works with time to spare: add a **second agent** that takes the finished
dispatch list and drafts a short radio message back to the field team for the single highest
priority item (e.g. "Dispatch team Alpha to Sector 4 immediately -- structural collapse with
signs of life"). The reference solution has a working version of this in
`draft_radio_message()` -- try it yourself first.
