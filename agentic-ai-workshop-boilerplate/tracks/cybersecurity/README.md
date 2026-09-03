# Track C -- Cybersecurity: Catch the Intruder

**The story:** Your agent watches a stream of login attempts (mocked: timestamp, IP address,
username, success/failure -- no real network traffic, no real logs). It reviews the whole
stream and flags suspicious patterns: brute-force attempts, impossible-travel logins (the same
person "logging in" from two far-apart places within minutes), and repeated failures. Then it
drafts a short incident report explaining its reasoning.

## What "done" looks like

- The agent reviews the full mock login stream.
- It flags every suspicious pattern it finds, with a type (brute force / impossible travel /
  repeated failures), a severity, and a one-sentence reasoning a human analyst could trust.
- You get a short plain-text incident report summarizing what it found.

**Demo moment:** with your agent working, slip an obvious brute-force sequence into the stream
live (see the bottom of the file) and watch it get caught and explained.

## Where to start

Open `starter/intruder_watch.py`. It already has:

- The mock login stream and a mock IP-to-location lookup
- `get_login_stream` and `lookup_ip_location` -- both fully working tools
- The full agent loop (`run_agent_until_done`) -- identical to phase_04, same pattern you
  already know

You need to fill in two `TODO`s:

1. `flag_incident` -- a few lines, append a dict to a list.
2. `INVESTIGATION_GOAL` -- the prompt that tells the agent what counts as suspicious and what
   to do about it. This is the real exercise. Use the cheat sheet's prompt template: goal,
   constraints (what counts as each pattern type), plan-first.

If the agent misses an obvious attack or flags something harmless, that's a prompt problem --
go make `INVESTIGATION_GOAL` more specific about what each pattern actually looks like.

## If you're stuck

Compare against `reference_solution/intruder_watch.py`.

## Stretch goal

If your core loop works with time to spare: add a step that drafts a short alert email to the
security team for the single highest-severity incident found (same idea as the radio-message
stretch in the Robotics track -- a second, tool-free LLM call that turns a decision you've
already made into a message for a human). The reference solution has a working version in
`draft_alert_email()`.
