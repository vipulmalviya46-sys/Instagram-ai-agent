"""Agent 3: pulls performance data and explains what to do next."""
import json

import brain
import instagram_api as ig

SYSTEM = """You are an Instagram growth analyst. Be specific and quantitative.
Base conclusions only on the data given; say when the sample is too small."""


def collect(limit: int = 20) -> dict:
    account = ig.get_account_info()
    posts = ig.get_recent_media(limit)
    for p in posts:
        p["insights"] = ig.get_media_insights(p["id"])
    return {"account": account, "posts": posts}


def report(limit: int = 20) -> str:
    data = collect(limit)
    prompt = (
        "Analyze this Instagram data. Give: (1) 3 key findings, (2) best and worst "
        "posts and why, (3) best format/topic/timing patterns, (4) 5 concrete "
        "actions for next week.\n\nDATA:\n" + json.dumps(data, default=str)[:60000]
    )
    return brain.ask(SYSTEM, [{"role": "user", "content": prompt}], max_tokens=1500)
