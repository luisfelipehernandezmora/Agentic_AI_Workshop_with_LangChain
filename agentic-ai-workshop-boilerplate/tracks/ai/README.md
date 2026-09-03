# Track B -- AI / General: The Study Group That Never Sleeps

**The story:** You give the agent a course topic. One agent drafts an explanation of it. A
second agent plays a skeptical examiner and pokes real holes in that explanation. A third
agent takes the criticism and produces a corrected final answer. You watch the whole
draft -> challenge -> revise exchange happen live.

This is the most technically ambitious track today: it's **multi-agent**, not single-agent.
That just means several separate LLM calls, each with a different role, talking to each other
in sequence -- not one bigger or scarier concept, just more of the same idea repeated.

## What "done" looks like

- You supply a topic (anything from your coursework -- "binary search," "SQL injection,"
  "supply and demand," whatever).
- You see three distinct outputs printed: the draft explanation, the examiner's critique, and
  the revised final answer.
- The revision visibly fixes what the examiner raised -- if it doesn't, your examiner's prompt
  probably isn't critical enough yet.

**Demo moment:** run it live on a topic someone in the room supplies, and narrate the draft ->
challenge -> revise exchange as it prints.

## Where to start

Open `starter/study_group.py`. It already has:

- `explain_concept` (Agent 1) fully working -- a plain LLM call with a "patient tutor" role
  set via a `SystemMessage`. No tools needed here; not every agent call requires one.
- The `save_final_answer` tool and the loop that calls it, already wired up.

You need to fill in two `TODO`s:

1. `challenge_explanation` (Agent 2) -- write the examiner's `SystemMessage`. This is the
   whole exercise: a vague "check this explanation" prompt gets you a rubber stamp ("looks
   good!"). Tell it explicitly to find at least one real flaw, oversimplification, or missing
   caveat.
2. `revise_explanation` (Agent 3) -- write the reviser's `SystemMessage`. Tell it to fix every
   point the examiner raised, and to call `save_final_answer` once it's satisfied.

If your examiner keeps saying "this is correct, no notes" -- that's a prompt problem. Make it
more explicitly adversarial.

## If you're stuck

Compare against `reference_solution/study_group.py`.

## Running short on time? Use the 2-agent fallback

If Agent 3 is giving you trouble, or you're running low on time: drop it. Have Agent 1
revise its *own* work using the examiner's critique, instead of adding a separate third agent.
Same idea, one fewer LLM call. The reference solution has a working version in
`run_study_group_two_agents()` -- switch to it by calling that function instead of
`run_study_group()` at the bottom of the file.
