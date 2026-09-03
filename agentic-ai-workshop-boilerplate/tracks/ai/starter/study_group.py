"""
TRACK B -- AI / General: The Study Group That Never Sleeps

Run it:
    python study_group.py

THE STORY
----------
You give the agent a course topic. One agent drafts an explanation. A second agent plays a
skeptical examiner and pokes real holes in it. A third agent takes the criticism and produces
a corrected final answer. You watch draft -> challenge -> revise happen live.

This is MULTI-agent: several separate LLM calls, each with a different role (set via a
SystemMessage), talking to each other in sequence. Not every agent call needs tools -- Agents
1 and 2 here are just plain generation with a role attached. We only reach for a tool at the
very end, to save the group's final answer.

WHAT'S ALREADY DONE FOR YOU
------------------------------
- `explain_concept` (Agent 1) -- fully working. Study this one closely: it's the pattern for
  "give an LLM call a role" that Agents 2 and 3 both reuse.
- `save_final_answer` -- a tool, and the loop in `revise_explanation` that calls it, already
  wired up.

WHAT YOU NEED TO BUILD (look for "TODO")
-------------------------------------------
1. `challenge_explanation` (Agent 2) -- write the examiner's SystemMessage. This is the real
   exercise: tell it explicitly to find at least one real flaw. A vague prompt here just gets
   you a rubber stamp ("looks good!").
2. `revise_explanation` (Agent 3) -- write the reviser's SystemMessage. Tell it to fix every
   point the examiner raised.
3. `TOPIC` at the bottom -- pick something from your own coursework.

Running short on time? See the 2-agent fallback at the bottom of this file -- drop Agent 3
and have Agent 1 revise its own work instead.
"""

import sys

# Windows terminals default to a legacy codepage (cp1252) that can't print
# a lot of Unicode the model might return in its answers (smart quotes,
# em dashes, narrow spaces, etc.) and will crash with UnicodeEncodeError
# the moment it tries. Force UTF-8 output so that never happens, on any OS.
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model=os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b"),
    temperature=0,
)

# Not every agent call needs tools -- explaining and critiquing are just
# generation tasks. We only reach for a tool at the very last step: saving
# the group's final, agreed-upon answer.
study_log = []


@tool
def save_final_answer(topic: str, final_explanation: str) -> str:
    """Save the study group's final, agreed-upon explanation for a topic,
    after it has been drafted, challenged, and revised. Call this exactly
    once, after you are satisfied the explanation fixes every criticism
    that was raised."""
    study_log.append({"topic": topic, "final_explanation": final_explanation})
    return "Saved."


tools = [save_final_answer]
llm_with_tools = llm.bind_tools(tools)
tools_by_name = {t.name: t for t in tools}


def explain_concept(topic: str) -> str:
    """AGENT 1 -- Explainer. A plain LLM call: no tools, just a role (set
    via SystemMessage) and a question. This is the pattern Agents 2 and 3
    both reuse below -- copy this shape when you write their prompts."""
    messages = [
        SystemMessage(content=(
            "You are a patient tutor explaining concepts to first-year "
            "university students. Explain clearly in 3-5 sentences. Avoid "
            "jargon; if you must use a technical term, briefly define it."
        )),
        HumanMessage(content=f"Explain: {topic}"),
    ]
    return llm.invoke(messages).content


def challenge_explanation(topic: str, explanation: str) -> str:
    """AGENT 2 -- Skeptical Examiner. TODO: write this agent's persona
    below. It reads the topic and Agent 1's explanation, and must find
    1-3 concrete problems: oversimplifications, missing caveats, or
    things that are flat wrong. Tell it explicitly to find at least one
    flaw -- otherwise it'll just say "looks good!" every time."""
    messages = [
        SystemMessage(content=(
            "TODO: write the examiner's persona and instructions here. "
            "Make it genuinely critical, not a rubber stamp."
        )),
        HumanMessage(content=f"Topic: {topic}\n\nExplanation to critique:\n{explanation}"),
    ]
    return llm.invoke(messages).content


def revise_explanation(topic: str, explanation: str, critique: str) -> str:
    """AGENT 3 -- Reviser. TODO: write this agent's persona below. It sees
    the ORIGINAL explanation AND the critique, and must produce a
    corrected final version that fixes every point raised, then call
    save_final_answer. The tool-calling part below is already wired up
    for you -- you only need to write the SystemMessage."""
    messages = [
        SystemMessage(content=(
            "TODO: write the reviser's persona and instructions here. "
            "Tell it to fix every issue the examiner raised, and to call "
            "save_final_answer with the topic and its corrected "
            "explanation once it's done."
        )),
        HumanMessage(content=(
            f"Topic: {topic}\n\nOriginal explanation:\n{explanation}\n\n"
            f"Examiner's critique:\n{critique}"
        )),
    ]
    ai_message = llm_with_tools.invoke(messages)

    final_text = ai_message.content
    if ai_message.tool_calls:
        for tool_call in ai_message.tool_calls:
            result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            print(f"    -> {result}")
            final_text = tool_call["args"].get("final_explanation", final_text)
    return final_text


def run_study_group(topic: str) -> None:
    """The full 3-agent exchange: draft -> challenge -> revise."""
    print(f"\n=== TOPIC: {topic} ===")

    print("\n[Agent 1 -- Explainer] drafting...")
    draft = explain_concept(topic)
    print(draft)

    print("\n[Agent 2 -- Skeptical Examiner] challenging...")
    critique = challenge_explanation(topic, draft)
    print(critique)

    print("\n[Agent 3 -- Reviser] revising...")
    final = revise_explanation(topic, draft, critique)
    print(final)


# =========================================================================
# FALLBACK -- 2-agent version. If Agent 3 is giving you trouble, or you're
# short on time: drop it, and have Agent 1 revise its OWN work instead of
# adding a separate third agent. Same idea, one fewer LLM call.
# =========================================================================
def run_study_group_two_agents(topic: str) -> None:
    print(f"\n=== TOPIC: {topic} (2-agent fallback) ===")

    print("\n[Agent 1 -- Explainer] drafting...")
    draft = explain_concept(topic)
    print(draft)

    print("\n[Agent 2 -- Skeptical Examiner] challenging...")
    critique = challenge_explanation(topic, draft)
    print(critique)

    print("\n[Agent 1 -- Explainer, self-correcting] revising own work...")
    messages = [
        SystemMessage(content=(
            "You are the same tutor from before. Someone raised the "
            "following criticism of your explanation. Revise your own "
            "explanation to fix every point raised, in 3-5 sentences."
        )),
        HumanMessage(content=(
            f"Topic: {topic}\n\nYour original explanation:\n{draft}\n\n"
            f"Criticism:\n{critique}"
        )),
    ]
    revised = llm.invoke(messages).content
    print(revised)


if __name__ == "__main__":
    TOPIC = "TODO: put a topic here, e.g. 'binary search' or 'SQL injection'"
    run_study_group(TOPIC)

    # Short on time, or Agent 3 not cooperating? Comment out the line
    # above and use the 2-agent fallback instead:
    # run_study_group_two_agents(TOPIC)
