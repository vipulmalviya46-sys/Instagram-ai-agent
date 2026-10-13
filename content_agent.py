"""Agent 2: plans content, writes captions, publishes posts."""
import brain
import config
import instagram_api as ig

SYSTEM = f"""You are the social media manager for {config.BRAND_NAME}.
Voice: {config.BRAND_VOICE}
About the business: {config.BUSINESS_INFO}
You write Instagram content that is specific, hooky in the first line, and
honest (no fake claims)."""


def plan_week(goal: str = "grow engagement", posts: int = 7) -> list[dict]:
    prompt = f"""Create a {posts}-post Instagram content plan. Goal: {goal}.
Return a JSON list; each item has: day, format (reel|carousel|image|story),
topic, hook (first line), caption (full, with CTA), hashtags (5-10 list),
visual_idea (what to shoot/design)."""
    return brain.ask_json(SYSTEM, prompt, max_tokens=4000)


def write_caption(topic: str, tone: str = "") -> dict:
    prompt = f"""Write 3 caption variants for: {topic}. {('Tone: ' + tone) if tone else ''}
Return JSON: {{"variants": [{{"caption": "...", "hashtags": ["..."]}}]}}"""
    return brain.ask_json(SYSTEM, prompt, max_tokens=1500)


def publish(image_url: str, caption: str, hashtags: list[str] | None = None,
            confirm: bool = False) -> dict:
    """Publishes only when confirm=True, so a human approves every post."""
    full = caption + ("\n\n" + " ".join(f"#{h.lstrip('#')}" for h in hashtags) if hashtags else "")
    if not confirm:
        return {"status": "draft_only", "caption": full,
                "note": "Call again with confirm=true to publish."}
    return {"status": "published", "result": ig.publish_image(image_url, full)}
