# Agentic AI Workshop @ Amrita

A hands-on workshop that takes you from zero to a working AI agent in about
an hour, using Python, LangChain, and [Groq](https://groq.com) (a free,
very fast LLM API). No GPU and no real hardware/sensors required -- every
project runs on mocked data (CSV files, lists, strings) so it works on any
laptop.

## What's in this repo

| Path | What it's for |
|---|---|
| [`slides/`](slides/) | Slide deck, printable cheat sheet, and the live-coding narrative used during the session |
| [`agentic-ai-workshop-boilerplate/`](agentic-ai-workshop-boilerplate/) | The code: setup checker, step-by-step phases, and three track projects |

## 1. Get the cheat sheet

If you just want the quick-reference handout, grab
[`slides/AI_Agent_Workshop_Cheatsheet.pdf`](slides/AI_Agent_Workshop_Cheatsheet.pdf).
It's the same material as the phase files below, condensed to one page --
useful to keep open while you code, or to take away after the workshop.

The full slide deck is [`slides/AI_Agent_Workshop_Slides.pptx`](slides/AI_Agent_Workshop_Slides.pptx),
and [`slides/live_coding_narrative.md`](slides/live_coding_narrative.md) has the
script used to build the demo live, step by step.

## 2. Get a free Groq API key

The workshop runs entirely on Groq's free tier -- no credit card, no GPU.

1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Sign up (or log in)
3. Click **Create API Key** and copy it
4. Paste it into your `.env` file (see setup below) as `GROQ_API_KEY`

Do this *before* the workshop if you can, so build time isn't spent waiting
on signup emails.

## 3. Set up and run the code

Everything for setup and running agents lives in
[`agentic-ai-workshop-boilerplate/`](agentic-ai-workshop-boilerplate/) --
its own [README](agentic-ai-workshop-boilerplate/README.md) has the full
details, but the short version:

```bash
cd agentic-ai-workshop-boilerplate

# create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# install dependencies
pip install -r requirements.txt

# create your .env file and add the Groq key from step 2
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux

# verify everything works before the session starts
python phase_00_setup/check_environment.py
```

If that last command prints `All checks PASSED`, you're ready to go.

## 4. Learn step by step

Work through the numbered phases in order -- each one is a small,
heavily-commented, standalone script that proves one new concept:

| Phase | File | What it proves |
|---|---|---|
| 0 | `phase_00_setup/check_environment.py` | Your setup + Groq key actually work |
| 1 | `phase_01_first_agent/hello_agent.py` | The core agent loop, one tool |
| 2 | `phase_02_add_a_tool/agent_with_tool.py` | Adding a second tool (giving your agent a new skill) |
| 3 | `phase_03_memory/agent_with_memory.py` | The agent remembering earlier turns |
| 4 | `phase_04_multi_step_task/agent_task_chain.py` | Looping through a whole list until the agent decides it's done |

Run any phase directly, e.g. `python phase_01_first_agent/hello_agent.py`.
You don't need to finish earlier phases to run a later one.

## 5. Build your own agent (the track projects)

Once you know the pattern, pick one track under
`agentic-ai-workshop-boilerplate/tracks/` and build it end to end:

- **`tracks/robotics/`** -- Rescue Drone Triage Agent
- **`tracks/ai/`** -- The Study Group That Never Sleeps (multi-agent)
- **`tracks/cybersecurity/`** -- Catch the Intruder

Each track has a `starter/` scaffold to build from and a
`reference_solution/` to compare against once you've had a go. When you
want to start a brand-new agent from scratch, copy
`template/new_agent_template.py` -- same pattern, with `TODO` markers
instead of a finished example.

## Troubleshooting

Common Groq/setup issues (invalid key, rate limits, retired models,
`ModuleNotFoundError`, tool-calling not triggering) are covered in the
[boilerplate README's Troubleshooting section](agentic-ai-workshop-boilerplate/README.md#4-troubleshooting-common-groq-key-issues).
