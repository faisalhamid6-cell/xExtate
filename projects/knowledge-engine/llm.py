"""
llm.py — A tiny "brain" abstraction for Mnemo, the Knowledge Engine.

Why this file exists
--------------------
We want ONE simple way to ask an AI a question, no matter what is running
underneath. So we define a small base class `LLMClient` with a single method:
`complete(prompt) -> str`.

There are two real versions:
  1. DemoClient  — needs NO setup, NO internet, NO API key. It returns simple
     stub text on purpose. In demo mode the agents do their own smart
     heuristics (cosine search, templates, keyword checks), so the "AI brain"
     is optional. This is what lets the demo run with ZERO installs.
  2. GeminiClient — talks to Google's Gemini model. It only runs if you have a
     GEMINI_API_KEY. We import the Google library LAZILY (inside the method)
     so that a missing package can NEVER break demo mode.

The `get_client()` factory at the bottom decides which one to use.
"""

import os


class LLMClient:
    """Base class. Every client must know how to turn a prompt into text."""

    def complete(self, prompt: str) -> str:
        """Take a text prompt, return the model's text answer."""
        raise NotImplementedError("Subclasses must implement complete().")


class DemoClient(LLMClient):
    """
    The zero-setup client used for the live demo.

    It returns a simple stub string. The agents detect demo mode and fall back
    to their built-in heuristics (bag-of-words cosine search, templated
    article synthesis, and keyword contradiction checks). No real AI call is
    made, so demo mode works with ZERO installs and ZERO API keys.
    """

    def complete(self, prompt: str) -> str:
        # No real AI call. Agents will use their own logic instead.
        return "[demo-mode] (no live model — agents use built-in heuristics)"


class GeminiClient(LLMClient):
    """
    The "live AI" client, powered by Google Gemini.

    This is the future upgrade path. It is fully written but only used when a
    GEMINI_API_KEY environment variable is present. The Google library is
    imported INSIDE complete() so that demo mode never depends on it.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model_name = model_name

    def complete(self, prompt: str) -> str:
        # LAZY IMPORT: only loaded when we actually call Gemini. This means the
        # `google-generativeai` package is NOT required for demo mode.
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model_name)
        response = model.generate_content(prompt)
        # `.text` holds the model's written answer.
        return response.text or ""


def get_client() -> LLMClient:
    """
    Decide which brain to use.

    - If GEMINI_API_KEY is set in the environment, use real Gemini.
    - Otherwise, fall back to the zero-setup DemoClient.

    We print a friendly line so the person watching the demo knows which mode
    is running.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if api_key:
        print("🤖 Using Gemini (live AI mode)")
        return GeminiClient(api_key=api_key)

    print("🧪 DEMO mode (no API key needed)")
    return DemoClient()
