# Agentic AI Workshop -- Boilerplate

Everything you need to build a working AI agent in the next hour, using
Python, LangChain, and Groq (a free, very fast LLM API). No GPU, no real
hardware/sensors -- every project uses mocked data (CSV, lists, strings).

## 1. Setup (do this before the workshop if you can)

```bash
# 1. Clone or download this folder, then move into it
cd agentic-ai-workshop-boilerplate

# 2. Create a virtual environment (recommended but not required)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file from the example
cp .env.example .env          # Mac/Linux
copy .env.example .env         # Windows

# 5. Get a FREE Groq API key at https://console.groq.com/keys
#    (sign up, click "Create API Key", paste it into .env)

# 6. Verify everything works BEFORE the build session starts
python phase_00_setup/check_environment.py
```

If step 6 prints `All checks PASSED`, you're ready. If it fails, read the
printed message -- it tells you exactly what's wrong and how to fix it
(see also Troubleshooting below).

## 2. The phase map

Work through these in order during the demo, or jump straight to
whichever one matches your remaining time if you fall behind:

| Phase | File | What it proves |
|---|---|---|
| 0 | `phase_00_setup/check_environment.py` | Your setup + Groq key actually work |
| 1 | `phase_01_first_agent/hello_agent.py` | The core agent loop, one tool |
| 2 | `phase_02_add_a_tool/agent_with_tool.py` | Adding a second tool (the pattern for "give your agent a new skill") |
| 3 | `phase_03_memory/agent_with_memory.py` | The agent remembering earlier turns |
| 4 | `phase_04_multi_step_task/agent_task_chain.py` | Looping through a whole list until the agent decides it's done |

Run any phase directly, e.g.:

```bash
python phase_01_first_agent/hello_agent.py
```

Each phase file is heavily commented and runs standalone -- you don't need
to have finished the earlier phases to run a later one.

## 3. Your track project

Pick one track under `tracks/`:

- `tracks/robotics/` -- Rescue Drone Triage Agent
- `tracks/ai/` -- The Study Group That Never Sleeps (multi-agent)
- `tracks/cybersecurity/` -- Catch the Intruder

Each track has:

- `starter/` -- a scaffold to build from (start here)
- `reference_solution/` -- a working end state, for the demo and for you
  to compare against if you get stuck (no peeking until you've tried!)

When you're ready to start a brand-new agent from scratch (today or
after the workshop), copy `template/new_agent_template.py` -- it's the
same pattern with `TODO` markers instead of a finished example.

## 4. Troubleshooting: common Groq key issues

**"Your API key was rejected (invalid or revoked)"**
You probably copy-pasted an extra space, or the key was regenerated.
Get a fresh one at https://console.groq.com/keys and replace the value
in `.env` (not `.env.example`).

**"The model '...' isn't available" / "decommissioned"**
Groq retires older models faster than most providers. Check the current
list at https://console.groq.com/docs/models and update `GROQ_MODEL` in
your `.env`. `qwen/qwen3.8-27b` is the default this workshop is
built against.

**"Groq says you're rate-limited (429)"**
Free-tier keys have per-minute request/token limits. With 120 people
hitting Groq at once during the live demo, you may see this briefly --
wait ~30-60 seconds and retry. If it persists during your own building
time, it usually means a loop is calling the LLM far more often than
expected (check for an infinite `while True` without a break condition).

**Nothing happens / hangs forever**
Check your internet connection. Groq's whole pitch is speed -- a normal
call should return in under 2 seconds. Anything that hangs much longer
is a network issue, not a "thinking" LLM.

**"Tool was never called" even though it obviously should have been**
Not every Groq-hosted model supports tool-calling. Confirm `GROQ_MODEL`
in your `.env` is set to a tool-calling-capable model (the default is).
Also check your tool's docstring actually describes when to use it --
a vague docstring is the #1 cause of an agent ignoring a tool it has.

**`ModuleNotFoundError` for `langchain_groq`, `dotenv`, or `groq`**
You forgot to `pip install -r requirements.txt`, or you're not in the
virtual environment you installed it into. Re-run
`python phase_00_setup/check_environment.py` -- it checks this for you.

## 5. A note if you're using an AI-assisted IDE (Antigravity, etc.)

Every phase file follows the exact same structure: define tools -> set up
the LLM -> run a loop that calls the LLM, executes any requested tools,
and feeds the results back. When you ask your AI pair-programmer to add a
feature, point it at the phase file closest to what you need (see the
table above) and ask it to follow that pattern -- it will produce far
more correct code than if you describe the feature from scratch.
