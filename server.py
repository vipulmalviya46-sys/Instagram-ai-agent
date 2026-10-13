"""FastAPI server: Instagram webhook + endpoints for content and analytics agents."""
import hashlib
import hmac

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel

import analytics_agent
import config
import content_agent
import dm_agent

app = FastAPI(title="Instagram AI Agent")


# ---------- Webhook (DMs + comments) ----------
@app.get("/webhook")
def verify(request: Request):
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and q.get("hub.verify_token") == config.VERIFY_TOKEN:
        return Response(content=q.get("hub.challenge", ""), media_type="text/plain")
    raise HTTPException(403, "Verification failed")


def _valid_signature(body: bytes, header: str | None) -> bool:
    if not config.APP_SECRET:
        return True  # dev mode; set APP_SECRET in production
    if not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(config.APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


@app.post("/webhook")
async def webhook(request: Request, bg: BackgroundTasks):
    body = await request.body()
    if not _valid_signature(body, request.headers.get("X-Hub-Signature-256")):
        raise HTTPException(403, "Bad signature")
    payload = await request.json()

    for entry in payload.get("entry", []):
        # Direct messages
        for m in entry.get("messaging", []):
            msg = m.get("message", {})
            sender = m.get("sender", {}).get("id")
            if msg.get("is_echo") or not msg.get("text") or not sender:
                continue
            if sender == config.IG_USER_ID:
                continue
            bg.add_task(dm_agent.handle_dm, sender, msg["text"])
        # Comments
        for ch in entry.get("changes", []):
            if ch.get("field") == "comments":
                v = ch.get("value", {})
                if v.get("id") and v.get("text"):
                    bg.add_task(dm_agent.handle_comment, v["id"], v["text"],
                                v.get("from", {}).get("id", ""))
    return {"status": "ok"}


# ---------- Content agent ----------
class PlanReq(BaseModel):
    goal: str = "grow engagement"
    posts: int = 7


class CaptionReq(BaseModel):
    topic: str
    tone: str = ""


class PublishReq(BaseModel):
    image_url: str
    caption: str
    hashtags: list[str] = []
    confirm: bool = False


@app.post("/content/plan")
def content_plan(req: PlanReq):
    return content_agent.plan_week(req.goal, req.posts)


@app.post("/content/caption")
def content_caption(req: CaptionReq):
    return content_agent.write_caption(req.topic, req.tone)


@app.post("/content/publish")
def content_publish(req: PublishReq):
    return content_agent.publish(req.image_url, req.caption, req.hashtags, req.confirm)


# ---------- Analytics agent ----------
@app.get("/analytics/report")
def analytics_report(limit: int = 20):
    return {"report": analytics_agent.report(limit)}


@app.get("/health")
def health():
    return {"ok": True}
