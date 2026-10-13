"""Claude wrapper used by all three agents."""
import json
import anthropic

import config

_client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)


def ask(system: str, messages: list[dict], max_tokens: int = 800) -> str:
    resp = _client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=messages,
    )
    return "".join(b.text for b in resp.content if b.type == "text").strip()


def ask_json(system: str, prompt: str, max_tokens: int = 2000):
    """Ask for strict JSON and parse it."""
    text = ask(
        system + "\nReturn ONLY valid JSON, no markdown fences, no commentary.",
        [{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
    )
    text = text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(text)
