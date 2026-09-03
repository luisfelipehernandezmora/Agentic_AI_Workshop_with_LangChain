"""
PHASE 0 -- Environment check.

Run this FIRST, before you touch any other phase:

    python phase_00_setup/check_environment.py

It checks four things, in order, and stops at the first failure so you know
exactly what to fix:

    1. Python version is new enough
    2. Required libraries are installed (requirements.txt)
    3. A .env file exists with GROQ_API_KEY set
    4. That key actually works -- we make one tiny real call to Groq

That last step matters: a missing/typo'd/expired key will otherwise blow up
in the middle of your build later, which is a much worse time to debug it.
This script catches it now, in 5 seconds, with a clear message.

Nothing here needs editing. If everything prints PASS, move on to
phase_01_first_agent.
"""

import os
import sys


def check_python_version() -> bool:
    print("[1/4] Checking Python version...", end=" ")
    if sys.version_info < (3, 9):
        print("FAIL")
        print(
            f"      You have Python {sys.version_info.major}.{sys.version_info.minor}, "
            "but this workshop needs 3.9 or newer."
        )
        print("      Install a newer Python from https://www.python.org/downloads/ "
              "and re-run this script.")
        return False
    print(f"PASS  (Python {sys.version_info.major}.{sys.version_info.minor})")
    return True


def check_libraries_installed() -> bool:
    print("[2/4] Checking required libraries are installed...", end=" ")
    missing = []
    for module_name in ["dotenv", "langchain", "langchain_groq", "groq"]:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(module_name)

    if missing:
        print("FAIL")
        print(f"      Missing: {', '.join(missing)}")
        print("      Fix: run this from the repo root (with your virtual environment active):")
        print("          pip install -r requirements.txt")
        return False
    print("PASS")
    return True


def check_env_file_and_key_present() -> bool:
    print("[3/4] Checking .env file and GROQ_API_KEY...", end=" ")
    from dotenv import load_dotenv

    # load_dotenv() looks for a ".env" file in the current directory (or parents)
    # and loads its contents into os.environ -- this is how the key gets from
    # the file into your Python process without ever being hardcoded in code.
    load_dotenv()

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key.strip() == "" or api_key == "your_groq_api_key_here":
        print("FAIL")
        print("      No real GROQ_API_KEY found in your environment.")
        print("      Fix:")
        print("        1. Copy the example file:  cp .env.example .env   (Windows: copy .env.example .env)")
        print("        2. Get a free key at https://console.groq.com/keys")
        print("        3. Paste it into .env as:  GROQ_API_KEY=gsk_your_real_key_here")
        return False
    print("PASS")
    return True


def check_key_actually_works() -> bool:
    print("[4/4] Checking your Groq API key actually works (live call)...", end=" ")
    import os as _os

    from groq import Groq

    api_key = _os.getenv("GROQ_API_KEY")
    model = _os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    client = Groq(api_key=api_key)

    try:
        # Smallest, cheapest possible real request -- just enough to prove
        # the key + model combination is valid before anyone starts building.
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say OK"}],
            max_tokens=5,
        )
    except Exception as e:  # noqa: BLE001 -- we want to catch and explain ANY failure here
        print("FAIL")
        message = str(e)

        if "401" in message or "invalid_api_key" in message.lower():
            print("      Your API key was rejected (invalid or revoked).")
            print("      Fix: generate a fresh key at https://console.groq.com/keys and update .env")
        elif "404" in message or "does not exist" in message.lower() or "decommissioned" in message.lower():
            print(f"      The model '{model}' isn't available on your account (or was retired).")
            print("      Fix: check current model names at https://console.groq.com/docs/models")
            print("           and update GROQ_MODEL in your .env file.")
        elif "429" in message:
            print("      Groq says you're rate-limited (too many requests right now).")
            print("      Fix: wait a minute and re-run this script. Free-tier limits reset quickly.")
        else:
            print("      Unexpected error talking to Groq:")
            print(f"      {message}")
            print("      Fix: check your internet connection, then re-run this script.")
        return False

    print("PASS")
    return True


def main() -> None:
    print("=" * 60)
    print("Agentic AI Workshop -- Environment Check")
    print("=" * 60)

    checks = [
        check_python_version,
        check_libraries_installed,
        check_env_file_and_key_present,
        check_key_actually_works,
    ]

    for check in checks:
        if not check():
            print()
            print("Environment check FAILED. Fix the issue above and re-run this script.")
            sys.exit(1)
        print()

    print("=" * 60)
    print("All checks PASSED. You're ready for phase_01_first_agent.")
    print("=" * 60)


if __name__ == "__main__":
    main()
