# AI Agent Development Workshop — Presentation Content

Amrita University · Sept 9, 2026 · 2:00–2:30 PM slot (slides) + 2:30–2:45 PM (live-code demo)
Audience: Robotics & AI first-years, S3 Cybersecurity, MTech first-years — mixed Python skill, many with none.

This is the **content and speaker-note draft** for the slide deck — review and edit this file first.
Once approved, this gets built into the actual .pptx with the pptx skill. Nothing here is final wording.

Format per slide: **On-slide content** (what's visually on the slide) then *Speaker notes* (what you say —
not meant to be printed on the slide itself).

Note on scope: this expands the original 14-slide outline to 21 slides, to fold in a dedicated LangChain
basics section, a granular phase-by-phase code walkthrough (phases 0→4), a closing "meta" slide, and a
real-world workflow section (below). Confirmed OK to run past 30 minutes for this — it's a teaching
session, not a timed pitch.

---

## 1. Title

**On-slide:**
- AI Agent Development Workshop
- Building your first LLM agent — LangChain + Groq
- Ing. Luis Felipe Hernández Mora · Universidad de Costa Rica
- Guest session · Amrita University · Sept 9, 2026

*Speaker notes:* Quick welcome. Set expectations: fully hands-on, nobody needs prior agent-building
experience, and by 4:00 PM everyone will have run a real agent they built themselves.

---

## 2. Why this matters

**On-slide:**
- Job postings mentioning "Agentic AI" skills grew **~280% in one year** — 0.06% → 0.23% of all US postings
  (2024→2025), roughly 90,000 postings *(Lightcast / Statista, 2025)*
- Gartner: **40% of enterprise applications** are expected to include task-specific AI agents by end of
  2026 — up from under 5% in 2025
- Right now there are an estimated **~3.4 open AI-related roles for every qualified candidate** — this is a
  real shortage, not hype *(Second Talent / industry hiring data, 2025–2026)*
- It cuts across all three specializations in this room:
  - Robotics → pairing classical control with LLM-driven decisions
  - AI/ML → the role is shifting from "train a model" to "build an agent around one"
  - Cybersecurity → both defending against agents and building them for defense

*Speaker notes:* This isn't a niche skill for one track — it's relevant whether you end up doing robotics,
general ML, or security work. Frame it as: today you're not learning a toy, you're doing the thing
companies are currently hiring for, and the numbers back that up — the postings are growing much faster
than the talent pool.

*Sources (put as small footnote text on the slide, or keep in speaker notes only — your call):*
[Statista: Growth in AI job postings by specialized skill](https://www.statista.com/chart/amp/36200/growth-in-number-of-ai-job-postings-in-the-us-by-specialized-skills/),
[Agentic AI hiring boom 2026](https://jobsbyculture.com/blog/agentic-ai-hiring-boom-2026),
[Belitsoft: AI agent development forecast 2026 (citing Gartner)](https://www.barchart.com/story/news/1204699/belitsoft-releases-ai-agent-development-forecast-2026-40-of-enterprise-applications-to-include-task-specific-agents-by-year-end),
[Second Talent: Global AI talent shortage statistics 2026](https://www.secondtalent.com/resources/global-ai-talent-shortage-statistics/)

---

## 3. What is an agent? (vs. a plain LLM call)

**On-slide:**
- A plain LLM call: prompt in → text out. One shot, fixed.
- An agent: the LLM can ask to run a function ("tool"), see what comes back, and decide again.
- Diagram (simple loop, describe verbally if not drawn):
  `Input → LLM decides → [maybe: run a tool → feed result back] → LLM decides again → Final answer`

*Speaker notes:* The key word is "decide." In a plain LLM call, you write 100% of the control flow. In an
agent, the model itself decides at runtime whether it needs more information before it can answer. That
handoff of control is the entire idea — everything else today is detail on top of that one idea.

---

## 4. The two layers

**On-slide:**
- **Intelligence layer** — the LLM itself: language understanding, reasoning. Today: Groq-hosted Llama models.
- **Agentic layer** — everything wrapped around it: tools, memory, control flow (when to loop, when to stop).
  Today: your Python code + LangChain.

*Speaker notes:* This is the split that matters most. The intelligence layer is essentially rented — you
call an API, Groq runs the model. Almost everything you personally build today is the agentic layer. That's
the difference between "I called an API" and "I built an agent."

---

## 5. What can an agent do?

**On-slide:**
- **Retrieve** — look something up
- **Decide** — score, classify, choose an action
- **Act** — call a tool that actually does something
- **Chain** — repeat those steps until a goal is met

*Speaker notes:* Map this straight onto today's tracks so it's not abstract: the drone agent retrieves a
report and decides a priority; the study-group agents chain draft → critique → revise; the cybersecurity
agent retrieves login events and decides which ones are suspicious. Same four verbs, three different
stories.

---

## 6. The security caveat

**On-slide:**
- Coding your own agent is a great first step into practical AI — it is **not** automatically a secure one.
- Tools mean real actions. A bug here isn't just a wrong answer — it's a wrong *action*.
- Prompt injection: untrusted text (a log line, a webpage, a user message) can try to steer an agent's next
  tool call.
- More tools + more autonomy = a bigger attack surface, not automatically more caution.

*Speaker notes:* Aim this directly at the Cybersecurity cohort. Today's "Catch the Intruder" track uses an
agent defensively — but as you build it, also think adversarially: what if one of those login-attempt
strings were crafted to make the agent do something other than what you intended? You don't need to solve
that today, just start noticing it as a category of bug, not just "wrong output."

---

## 7. Why LangChain

**On-slide:**
- Python-first
- The current industry standard for building agents — most tutorials, job postings, interviews reference it
- A thin, well-documented layer over raw LLM API calls — the concepts transfer even if you switch providers
  later (OpenAI, Anthropic, a local model)

*Speaker notes:* Briefly acknowledge the landscape exists (LlamaIndex, raw SDKs, newer frameworks) without
detouring into a comparison — the point is LangChain is the most transferable thing to learn *today*, not
that it's the only option forever.

---

## 8. LangChain basics — the four moving parts

**On-slide:**
- **Chat model** — `ChatGroq`: LangChain's standard wrapper around a chat LLM. Same shape as `ChatOpenAI` /
  `ChatAnthropic` — swap providers later by changing one line.
- **Messages** — the conversation is a typed list: `HumanMessage`, `AIMessage`, `SystemMessage`,
  `ToolMessage`. This list is exactly what gets sent to the model, every single call.
- **Tools** — a plain Python function + `@tool` decorator + a docstring. The docstring is the *only* thing
  the model reads to decide when and how to use it.
- **Binding & responses** — `llm.bind_tools([...])` tells the model what it's allowed to request.
  `ai_message.tool_calls` comes back either empty (model just answered) or as a list of requested function
  calls with arguments.

*Speaker notes:* This vocabulary — chat model, message, tool, bind_tools, tool_calls — is the exact set of
words you'll point at over and over in the code in a minute. Worth saying explicitly: "there are only four
new concepts here, everything else is plain Python you already know."

---

## 9. The scaffold — repo tour

**On-slide:**
- Folder tree (`phase_00_setup` → `phase_04_multi_step_task` → `tracks/` → `template/`)
- One sentence: "Every phase from here follows the exact same loop: ask the model → check if it wants a
  tool → run the tool → feed the result back → ask again."

*Speaker notes:* This is the hinge slide before you switch to walking the actual code live. Tell them:
"I'm going to open the real files now — phase by phase — and everything after this slide is the same five
lines of loop logic, so once phase 1 clicks, phases 2 through 4 are just 'what got added,' not new
concepts."

---

## 10. Phase 0 — Environment Check

**On-slide:**
- `phase_00_setup/check_environment.py`
- Four checks, in order: Python version → libraries installed → `.env` / key present → **one real Groq
  call**
- Why the live call matters: catches a bad/expired key *now*, in 5 seconds — not mid-build, an hour from now

*Speaker notes:* Point out this is the file they should have already run before today. If anyone's showing a
FAIL right now, this is the moment to fix it, not during the build block. Briefly show the four `check_*`
function names and the pass/fail print style so they recognize the pattern.

---

## 11. Phase 1 — Your first agent (the core loop)

**On-slide:**
- `phase_01_first_agent/hello_agent.py`
- The loop, spelled out:
  1. LLM decides (`llm_with_tools.invoke(messages)`)
  2. Check `ai_message.tool_calls` — empty, or a request?
  3. If requested: **Python** runs the actual function (the LLM never executes code itself)
  4. Feed the result back as a `ToolMessage`
  5. Ask the LLM again → final answer
- One `@tool` function example: `get_word_count` — the docstring *is* the instruction

*Speaker notes:* This is the slide to slow down on — everything later is a variation of this exact loop.
Walk the docstring specifically: "the model has never seen this function's code, it only ever reads this
one sentence to decide when to call it." Show what happens if you ask it something that doesn't need the
tool at all (tool_calls comes back empty) versus something that does.

---

## 12. Phase 2 — Adding a tool

**On-slide:**
- `phase_02_add_a_tool/agent_with_tool.py`
- The loop code: **unchanged**, character for character, from phase 1
- What actually changed: one new `@tool` function (`lookup_student`), added to the `tools` list
- This is the entire pattern for "give your agent a new skill"

*Speaker notes:* Make the "nothing else changed" point explicit — maybe even scroll both files side by side
for a second. The takeaway they should walk away with: adding a capability to their track project later is
just "write a function, decorate it, add it to a list," not a bigger architectural change.

---

## 13. Phase 3 — Memory

**On-slide:**
- `phase_03_memory/agent_with_memory.py`
- The change, in one line: `conversation_history` is declared *outside* the function and **appended to**,
  never recreated
- No special "memory object" — memory is just a list that survives between calls

*Speaker notes:* Contrast with phases 1–2, where `messages = [...]` was rebuilt fresh every call — that's
why those agents "forgot" everything instantly. Ask rhetorically: "what's the simplest possible way to make
something remember? Don't throw it away." That's it.

---

## 14. Phase 4 — Chaining multiple steps

**On-slide:**
- `phase_04_multi_step_task/agent_task_chain.py`
- New idea: loop **rounds** of tool-calling, not just one — `for step in range(1, max_iterations + 1)`
- Stop condition: the LLM itself decides it's done (`tool_calls` comes back empty) — not you
- `max_iterations` is just a safety net, not the real stop signal

*Speaker notes:* This is the pattern every track project actually needs — processing a whole queue of drone
reports / login attempts / whatever, not just one item. Point at the `QUEUE_EMPTY` sentinel as the concrete
example of "how do you tell the agent it's done" — this is the one thing that trips people up when they
build their own version, so name it explicitly.

---

## 15. Today's three tracks

**On-slide:** (use the sharp one-liners, not generic descriptions)
- **Robotics** — *The Rescue Drone Triage Agent.* Damage reports come in after an earthquake; the agent
  ranks them into a live dispatch list. **Done** = paste in a new report live, watch it slot into the
  ranking with visible reasoning.
- **AI/General** — *The Study Group That Never Sleeps.* One agent explains a concept, a second attacks it,
  a third fixes it. **Done** = a visible draft → challenge → revise exchange, on a topic you supply live.
- **Cybersecurity** — *Catch the Intruder.* The agent watches a stream of login attempts and flags
  brute-force patterns and impossible travel. **Done** = slip in an obvious attack live and watch it get
  caught and explained.

*Speaker notes:* Pick whichever story matches your own background for the live-code demo at 2:30. Mention
the AI track is the most technically ambitious (3 agents) and has a documented fallback to 2 agents if a
group is short on time — so nobody should avoid it out of fear of running out of time.

---

## 16. Tools you need

**On-slide:**
- A free Groq API key — https://console.groq.com/keys
- Google Antigravity (or your preferred AI-assisted IDE)
- Both should already be set up — if not, do it in the next 2 minutes while I finish talking

*Speaker notes:* Give a short pause here for stragglers to get their key. This is also the moment to
mention `phase_00_setup/check_environment.py` again as the way to confirm the key actually works before
2:45.

---

## 17. How the next hour works

**On-slide:**
1. Clone the repo
2. Pick a track (or stay flexible — jump to any phase if you fall behind)
3. Build from `tracks/<your-track>/starter/`
4. Ask for help — me, a neighbor, your AI pair-programmer
5. 2–3 of you demo at 3:45

*Speaker notes:* Reassure the mixed-skill room explicitly: "if you don't finish, that's fine — jump to
whichever phase matches your remaining time, phase_00 through phase_04 each work standalone." Point at the
`reference_solution/` folder as a "look here if truly stuck," not a "copy this first."

---

## 18. One more thing

**On-slide:**
- This entire workshop — this slide deck, the phase-by-phase code, the track projects, the cheat sheet —
  was built by an AI agent (Claude Code), working with me as the human in the loop.
- Not a metaphor: an actual agent loop. It read the requirements, planned, wrote the code, checked its own
  work, and paused for my sign-off at checkpoints — the exact same loop you just watched in phases 1–4.

*Speaker notes:* Save this as a reveal, not something you mention earlier — let it land. Say something
like: "Everything you've looked at for the last 30 minutes was built this way. If an agent can build the
material for teaching you to build agents, think about what's possible once you're the one steering it."
Ties straight back to slide 2 — this isn't a hypothetical hiring trend, it's how this exact session got made.

---

## 19. How I actually build real projects with agentic AI

**On-slide:**
- Start with a long prompt describing the ENTIRE problem — often voice-dictated, not typed, so
  nothing gets left out for the sake of brevity.
- Feed in whatever already exists: a PRD, user stories, an architecture proposal, sometimes even a
  frontend someone else on the team (or the client) already built.
- Before any code gets written, ask for exactly two documents: a **plan** and a **task list**.

*Speaker notes:* This is the direct follow-up to the reveal on the previous slide — "here's literally
the method I used." Frame it as: the skill that actually matters isn't typing code fast, it's giving an
agent enough context and enough structure up front that it doesn't need fixing later. Mention explicitly
that you often dictate the initial prompt by voice — the point is capturing everything you know about the
problem, not writing elegant prose. This applies to real client/team work, not just today's toy tracks.

---

## 20. PLAN.md + TASKS.md — the two-document system

**On-slide:** (two-column comparison)
- **PLAN.md** — breaks the project into **phases**, ordered by logical dependency (you can't build
  phase 3 before phase 2's foundation exists). One paragraph per phase: what it covers, why it comes
  where it does.
- **TASKS.md** — the SAME phases, broken into specific, checkbox-able action items: "declare this API,"
  "build these N endpoints," "wire up this frontend route." Every phase ends with an explicit
  **definition of done** — what has to be true before moving to the next one.
- Then: execute **phase by phase** with an agentic coding assistant (e.g. Claude Code), checking off
  tasks as they complete. Dramatically fewer mistakes than "just start coding."

*Speaker notes:* Draw the connection explicitly: this is the exact same phase-based, dependency-ordered
thinking as today's `phase_00` → `phase_04` boilerplate, just scaled up to real, large projects. The
reason this works isn't magic — it's that the agent always knows which phase it's in, what "done" means
for that phase, and it never has to hold the entire project in its head at once. Encourage them to try
this on their own next project, even a class assignment: describe the whole problem, ask for a PLAN.md
and a TASKS.md before writing a line of code, then work through it phase by phase.

---

## 21. The takeaway + Let's build

**On-slide:**
- Cheat sheet (one page): the core steps, the prompt template, key links, "stuck at X → jump to phase Y,"
  and the PLAN.md/TASKS.md workflow from the last two slides
- `template/new_agent_template.py` — reusable scaffold for your next agent project, after today
- **Let's build.**

*Speaker notes:* Hand off to the 2:30 live-code demo here. Remind them the cheat sheet is what to keep open
on a second screen/phone while building, not something to read now.

---

## Status

- Granular phase walkthrough (slides 10–14): kept, confirmed.
- Slide 2 stats: added, sourced (see slide 2's source list) — flag if you'd rather cite different/primary
  reports instead of the aggregator sites the search turned up.
- Slide 1: name and affiliation filled in.
- Slide 18 added: reveal that this workshop's materials were built by an AI agent.
- Slides 19–20 added: the real-world PLAN.md/TASKS.md workflow for using agentic AI on actual projects,
  requested as a follow-on from the slide 18 reveal. Deck is now 21 slides.

Next: once you confirm this reads right, this becomes the actual .pptx via the pptx skill.
