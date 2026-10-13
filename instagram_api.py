"""Thin wrapper over the official Instagram Graph API."""
import time
import httpx

import config

_client = httpx.Client(timeout=30)


def _check(r: httpx.Response) -> dict:
    if r.status_code >= 400:
        raise RuntimeError(f"Instagram API error {r.status_code}: {r.text}")
    return r.json()


# ---------- Messaging ----------
def send_dm(recipient_id: str, text: str) -> dict:
    """Reply to a user. Only allowed within 24h of their last message."""
    r = _client.post(
        f"{config.GRAPH_URL}/{config.IG_USER_ID}/messages",
        params={"access_token": config.IG_ACCESS_TOKEN},
        json={"recipient": {"id": recipient_id}, "message": {"text": text[:1000]}},
    )
    return _check(r)


def reply_to_comment(comment_id: str, text: str) -> dict:
    r = _client.post(
        f"{config.GRAPH_URL}/{comment_id}/replies",
        params={"access_token": config.IG_ACCESS_TOKEN},
        data={"message": text[:2200]},
    )
    return _check(r)


def private_reply_to_comment(comment_id: str, text: str) -> dict:
    """Send a DM to someone who commented (one private reply per comment)."""
    r = _client.post(
        f"{config.GRAPH_URL}/{config.IG_USER_ID}/messages",
        params={"access_token": config.IG_ACCESS_TOKEN},
        json={"recipient": {"comment_id": comment_id}, "message": {"text": text[:1000]}},
    )
    return _check(r)


# ---------- Publishing ----------
def publish_image(image_url: str, caption: str) -> dict:
    """image_url must be a public JPEG URL."""
    c = _client.post(
        f"{config.GRAPH_URL}/{config.IG_USER_ID}/media",
        params={"access_token": config.IG_ACCESS_TOKEN},
        data={"image_url": image_url, "caption": caption},
    )
    container_id = _check(c)["id"]
    time.sleep(3)
    p = _client.post(
        f"{config.GRAPH_URL}/{config.IG_USER_ID}/media_publish",
        params={"access_token": config.IG_ACCESS_TOKEN},
        data={"creation_id": container_id},
    )
    return _check(p)


# ---------- Insights ----------
def get_recent_media(limit: int = 25) -> list[dict]:
    r = _client.get(
        f"{config.GRAPH_URL}/{config.IG_USER_ID}/media",
        params={
            "access_token": config.IG_ACCESS_TOKEN,
            "fields": "id,caption,media_type,timestamp,like_count,comments_count,permalink",
            "limit": limit,
        },
    )
    return _check(r).get("data", [])


def get_media_insights(media_id: str) -> dict:
    r = _client.get(
        f"{config.GRAPH_URL}/{media_id}/insights",
        params={
            "access_token": config.IG_ACCESS_TOKEN,
            "metric": "reach,saved,shares,total_interactions",
        },
    )
    try:
        data = _check(r).get("data", [])
    except RuntimeError:
        return {}
    return {m["name"]: m["values"][0]["value"] for m in data}


def get_account_info() -> dict:
    r = _client.get(
        f"{config.GRAPH_URL}/{config.IG_USER_ID}",
        params={
            "access_token": config.IG_ACCESS_TOKEN,
            "fields": "username,followers_count,follows_count,media_count",
        },
    )
    return _check(r)
