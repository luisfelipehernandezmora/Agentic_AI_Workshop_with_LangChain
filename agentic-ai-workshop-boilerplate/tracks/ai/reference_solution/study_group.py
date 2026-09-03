"""
TRACK B -- AI / General: The Study Group That Never Sleeps (REFERENCE SOLUTION)

Run it:
    python study_group.py

This is a working end state -- use it to demo from, or to compare against if your own version
in starter/ is stuck. Don't start here; start in starter/study_group.py.

Includes both the full 3-agent version and the 2-agent fallback.
"""

import sys

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
    """AGENT 1 -- Explainer. A plain LLM call: no tools, just a role."""
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
    """AGENT 2 -- Skeptical Examiner. Genuinely critical, not a rubber
    stamp: told explicitly to find real flaws or say why it can't."""
    messages = [
        SystemMessage(content=(
            "You are a skeptical exam board member reviewing a tutor's "
            "explanation of a course concept. Your job is to find "
            "problems, not to be nice. Look specifically for: "
            "(1) oversimplifications that hide an important exception, "
            "(2) missing caveats a student would need to avoid a common "
            "mistake, (3) anything that is simply incorrect. "
            "List 1-3 concrete issues as short bullet points. If you "
            "truly cannot find a real issue after checking carefully, say "
            "so explicitly and explain why the explanation holds up -- "
            "but default to looking hard for at least one genuine gap."
        )),
        HumanMessage(content=f"Topic: {topic}\n\nExplanation to critique:\n{explanation}"),
    ]
    return llm.invoke(messages).content


def revise_explanation(topic: str, explanation: str, critique: str) -> str:
    """AGENT 3 -- Reviser. Sees the original explanation AND the
    critique, fixes every point raised, then saves the final answer."""
    messages = [
        SystemMessage(content=(
            "You are the same tutor, revising your explanation after "
            "peer review. You will be given your original explanation "
            "and an examiner's critique of it. Rewrite the explanation "
            "so it directly addresses every issue the examiner raised, "
            "while staying clear and at the same 3-5 sentence length. "
            "Then call save_final_answer with the topic and your revised "
            "explanation. Call it exactly once."
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


def run_study_group_two_agents(topic: str) -> None:
    """FALLBACK -- 2-agent version. Agent 1 revises its own work instead
    of a separate third agent."""
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
    TOPIC = "binary search"
    run_study_group(TOPIC)

    print("\n\n>>> DEMO: same topic, 2-agent fallback for comparison <<<")
    run_study_group_two_agents(TOPIC)
