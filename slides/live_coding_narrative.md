# Live-Coding Narrative — Phases 0→4

This is your speaking script for walking the class through `phase_00` → `phase_04` live,
during the 2:00–2:30 slot (after the concept slides, before the 60-minute build). Every
terminal output quoted below is **real** — captured from actually running each file with the
final repo setup (`qwen/qwen3.8-27b` on Groq) — not a guess at what it "should" print. Read
through it once before the session so the real behavior doesn't surprise you live.

**How to use this doc:** don't read it verbatim on stage. Skim it once beforehand so the
beats are in your head, then talk naturally — the point is that nothing here should surprise
you when you actually run the command in front of the room.

---

## Before you open any file

Say this once, up front:

> "Everything today runs through Groq — it's a free, extremely fast API for open models.
> One thing about Groq specifically: they retire and rotate which models they host faster
> than most providers. The model this repo uses by default is `qwen/qwen3.8-27b` — not a
> Llama model, even though a lot of tutorials online default to Llama names. If you ever see
> a 'model decommissioned' error, that's not your code being broken, that's just Groq's
> lineup changing — check `console.groq.com/docs/models` and swap the name in your `.env`."

This pre-empts the single most likely "wait, why did the tutorial code use a different model
name" question before it derails your live demo.

---

## Phase 0 — Environment Check

**Say before running it:**

> "First file, before any agent logic at all: a script that checks your setup is actually
> ready. Four checks, and — this is the important part — the fourth one makes a REAL call to
> Groq. Not just 'is there a string in your .env file' — an actual live request. Watch."

**Run:**
```
python phase_00_setup/check_environment.py
```

**What appears on screen (verbatim, real output):**
```
============================================================
Agentic AI Workshop -- Environment Check
============================================================
[1/4] Checking Python version... PASS  (Python 3.14)

[2/4] Checking required libraries are installed... PASS

[3/4] Checking .env file and GROQ_API_KEY... PASS

[4/4] Checking your Groq API key actually works (live call)... PASS

============================================================
All checks PASSED. You're ready for phase_01_first_agent.
============================================================
```

**Say while/after it runs:**

> "Notice step 4 took a beat longer than the others — that's the network round-trip to Groq.
> That one extra second right now is the whole point of this file: if your key is wrong, or
> your `.env` has a typo, you find out in this one second, not forty minutes into your build
> when you're staring at a stack trace and don't know why. If ANYONE in the room sees a FAIL
> instead of this, raise your hand now — do not carry that into the next hour."

---

## Phase 1 — Your First Agent (the core loop)

This is the slide to slow down on. Everything after this is "the same thing, plus one more
idea." Open `phase_01_first_agent/hello_agent.py` and scroll to the `@tool` function first.

**Say, pointing at `get_word_count`:**

> "This is a tool. It's a completely normal Python function — count the words in a string,
> nothing fancy. The only unusual thing is this docstring, and I want you to really register
> this: the model never sees this function's code. Ever. It only reads this one sentence —
> 'Count how many words are in a piece of text' — and that sentence is the ONLY information
> it has to decide when to call this function. If your tool doesn't get called when you
> expect, 95% of the time the fix is 'write a better docstring,' not 'fix the code.'"

**Say, pointing at `llm.bind_tools(tools)`:**

> "This one line is the whole handoff. Before this line, it's just a chatbot. After this
> line, the model is allowed to ask us to run functions on its behalf."

**Run:**
```
python phase_01_first_agent/hello_agent.py
```

**What appears on screen (verbatim, real output):**
```
Thinking about: "How many words are in the sentence: The quick brown fox jumps over the lazy dog?"
Calling tool: get_word_count({'text': 'The quick brown fox jumps over the lazy dog'})
   -> tool result: 9
Final answer: The sentence contains **9 words**.
```

**Say while it runs, matching each printed line:**

> "Watch these four lines land one at a time. 'Thinking about' — that's us sending the
> question. 'Calling tool' — the model just decided, on its own, that it needs this function,
> and it even figured out the right argument to pass. THAT line right there is the entire
> concept of an agent. We didn't write an if-statement that says 'if the question contains
> the word how-many, call get_word_count.' The model decided that by itself. Then we run the
> function — that's Python, not the model, doing the counting — get 9 back, hand it to the
> model, and it writes the final sentence."

**Optional live tweak** (only if you have time / a confident room): change the question at the
bottom to something that obviously doesn't need the tool — e.g. `"What is the capital of
France?"` — rerun, and point out `Calling tool` never appears. That contrast is worth the 20
seconds it costs.

---

## Phase 2 — Adding a Tool

Open `phase_02_add_a_tool/agent_with_tool.py` side by side with phase_01 if your screen
allows it (or just say the next line confidently, you don't strictly need the split view).

**Say:**

> "I want you to notice something by absence: the loop code in this file — invoke, check
> tool_calls, run the tool, feed it back — is IDENTICAL to phase 1. Character for character.
> The only thing that changed is we wrote one more function, `lookup_student`, gave it a
> docstring, and added it to this list right here. That's it. That's the entire pattern for
> giving your agent a new capability, and it's the exact pattern you'll use in your track
> project every time you want your agent to do something new."

**Run:**
```
python phase_02_add_a_tool/agent_with_tool.py
```

**What appears on screen (verbatim, real output):**
```
Thinking about: "What program is bilal in, and what year?"
Calling tool: lookup_student({'name': 'bilal'})
   -> tool result: Bilal is a Year 3 student in Cybersecurity.
Final answer: Bilal is a Year 3 student in Cybersecurity.
```

**Say:**

> "Two tools bound now, and it picked the right one without being told which one to use. That
> choosing is also the model's job, not ours."

---

## Phase 3 — Memory

Open `phase_03_memory/agent_with_memory.py`. Point at the module-level `conversation_history = []`.

**Say:**

> "Here's the whole trick to memory, and I want it to feel almost anticlimactic: this list is
> declared OUTSIDE the function, at the top of the file, and every call APPENDS to it instead
> of replacing it. In phases 1 and 2, `messages` was built fresh inside the function every
> single time — so of course the agent forgot everything, we were throwing the conversation
> away on purpose without realizing it. The fix isn't a special memory class or a database.
> It's just: don't throw the list away."

**Run:**
```
python phase_03_memory/agent_with_memory.py
```

**What appears on screen (verbatim, real output — read the second exchange out loud, it's the
payoff):**
```
You said: "My name is Priya and I'm building the Cybersecurity track project."
Agent: Hi Priya! Great to meet you. I'd be happy to help with your Cybersecurity track project.

To give you the most useful guidance, could you share a bit more about what you're working on? For example:

- **What's the scope?** (e.g., a network security tool, a vulnerability scanner, a secure authentication system, a CTF challenge, a threat detection model, etc.)
- **What stage are you at?** (planning, design, implementation, testing, or troubleshooting)
- **What technologies/languages are you using?** (Python, Go, C, JavaScript, specific frameworks, etc.)
- **Any specific challenges or questions** you're facing right now?

Feel free to share as much or as little detail as you'd like, and I'll tailor my help accordingly.

You said: "What track am I working on, and what's my name?"
Agent: Your name is **Priya**, and you're working on the **Cybersecurity** track project.
```

**Heads-up — this is a real behavior you should be ready for, not a bug:** the model's FIRST
reply is chattier than you might expect — it asks Priya a bunch of clarifying questions
instead of a short "hi." That's just the model being helpful in its own way; it doesn't break
anything. Don't apologize for it or re-run hoping for a shorter answer — just keep talking
over it, or say:

> "Ignore how chatty that first answer is, that's just this model's personality. The part
> that matters is the SECOND question — I never told it my name or my track again, and..."
> *(let the second line print)* "...there it is. It remembered both, from two turns back.
> Nothing in my second message repeated that information — it's sitting in that list."

---

## Phase 4 — Chaining Multiple Steps

Open `phase_04_multi_step_task/agent_task_chain.py`. This is the one your tracks are actually
built on, so it's worth the extra thirty seconds.

**Say, before running:**

> "Every phase so far did AT MOST one round of 'call a tool, then answer.' Real tasks need
> several rounds in a row. Watch the step counter on the left as this runs — we're not
> capping this at one tool call anymore, we're looping until the MODEL decides there's
> nothing left to do."

**Run:**
```
python phase_04_multi_step_task/agent_task_chain.py
```

**What appears on screen (verbatim, real output — 10 steps, let it fully play out, it takes a
few seconds and that's fine, let the silence sit):**
```
--- Step 1 ---
get_next_sensor_reading({})
   -> Sensor A: reading 22.1C, normal range

--- Step 2 ---
record_finding({'reading': 'Sensor A: reading 22.1C, normal range', 'verdict': 'normal'})
   -> Logged: normal

--- Step 3 ---
get_next_sensor_reading({})
   -> Sensor B: reading 95.4C, DANGER threshold is 80C

--- Step 4 ---
record_finding({'reading': 'Sensor B: reading 95.4C, DANGER threshold is 80C', 'verdict': 'overheating - needs attention'})
   -> Logged: overheating - needs attention

--- Step 5 ---
get_next_sensor_reading({})
   -> Sensor C: reading 21.8C, normal range

--- Step 6 ---
record_finding({'reading': 'Sensor C: reading 21.8C, normal range', 'verdict': 'normal'})
   -> Logged: normal

--- Step 7 ---
get_next_sensor_reading({})
   -> Sensor D: no signal received

--- Step 8 ---
record_finding({'reading': 'Sensor D: no signal received', 'verdict': 'no data - check connection'})
   -> Logged: no data - check connection

--- Step 9 ---
get_next_sensor_reading({})
   -> QUEUE_EMPTY

--- Step 10 ---
Agent finished: The queue is now empty. Here's a summary of everything I found: ...
```

**Say, pointing at steps 9 and 10 specifically:**

> "Step 9 — it asked for the next reading, and got back this exact string, `QUEUE_EMPTY`.
> That string is a signal we invented, on purpose, so the agent has an unambiguous way to
> know it's done. Step 10 — no tool call at all, just a summary in plain English. THAT'S the
> stop condition. We never told it 'there are exactly four sensors, stop after four calls.'
> It figured out when to stop entirely from that one sentinel value. This exact pattern —
> drain a queue, get a clear 'empty' signal, summarize — is precisely what your track project
> does this afternoon, just with drone reports, or login attempts, or study topics instead of
> sensor readings."

**Bridge to the build block:**

> "That's the whole toolkit. Four ideas: a tool is a function plus a docstring; the model
> decides when to use it; a list that doesn't get thrown away is memory; and a loop that
> stops when tool_calls comes back empty is how you process a whole list of things. Every
> track this afternoon is those same four ideas wearing a different costume. Pick your track,
> open `starter/`, and go."

---

## If something goes visibly wrong live

- **A tool never gets called when you expect it to:** say "docstring problem, not a code
  problem" out loud — it's a real, common failure mode and naming it calms the room.
- **The model answers something PLAUSIBLE but WRONG:** these are not deterministic systems.
  Say so directly: "that's a real thing that happens — it's not a bug in our code, the model
  just got something wrong. This is exactly why phase_00 checks your setup separately from
  checking whether your PROMPT is good."
- **A run hangs longer than ~10 seconds:** that's Groq's network, not your laptop. Groq's
  whole pitch is speed, so it's rare — but if it happens, say so, and give it a few seconds
  before you consider re-running.
