# Instagram AI Agent

One service with three agents, built on Claude and the official Instagram Graph API:

| Agent | What it does | How it runs |
|---|---|---|
| **DM + Comment agent** | Answers DMs and comments, flags leads, hands off to a human when unsure | Webhook (`POST /webhook`) |
| **Content agent** | Weekly content plan, caption variants, publishes images (only after you confirm) | `POST /content/plan`, `/content/caption`, `/content/publish` |
| **Analytics agent** | Pulls account + post insights and writes an action report | `GET /analytics/report` |

## 1. Prerequisites

- Instagram **Business or Creator** account linked to a Facebook Page
- A Meta developer app (developers.facebook.com) with the Instagram product added
- Permissions: `instagram_business_basic`, `instagram_business_manage_messages`,
  `instagram_business_manage_comments`, `instagram_business_content_publish`,
  `instagram_business_manage_insights` (some need Meta App Review for public use;
  your own account works in development mode)
- An Anthropic API key
- Python 3.10+

## 2. Setup

```bash
pip install -r requirements.txt
cp .env.example .env      # fill in your keys and brand info
uvicorn server:app --port 8000
```

Meta needs a public HTTPS URL for the webhook. For local testing use a tunnel:
`ngrok http 8000` (or cloudflared), then in the Meta app dashboard:

1. Webhooks, Instagram: callback URL `https://<your-url>/webhook`, verify token = `VERIFY_TOKEN` from `.env`
2. Subscribe to `messages` and `comments`

## 3. Try it

```bash
# Content plan
curl -X POST localhost:8000/content/plan -H 'content-type: application/json' \
  -d '{"goal":"get more saves","posts":5}'

# Caption ideas
curl -X POST localhost:8000/content/caption -H 'content-type: application/json' \
  -d '{"topic":"new lavender candle launch"}'

# Publish (draft first, then confirm)
curl -X POST localhost:8000/content/publish -H 'content-type: application/json' \
  -d '{"image_url":"https://example.com/pic.jpg","caption":"New drop!","hashtags":["candles"],"confirm":false}'

# Analytics report
curl localhost:8000/analytics/report
```

Then DM your account from another Instagram profile to test the responder.

## 4. Important limits and rules

- DMs: you can reply only within **24 hours** of the user's last message.
- Comment private replies: one per comment, within 7 days.
- Images must be public JPEG URLs. Reels/carousels need extra container calls (extend `instagram_api.py`).
- Use only official APIs. Automating the personal-app UI violates Instagram terms and risks a ban.
- Tell users they are chatting with an AI if your region or policy requires it.

## 5. Before production

- Replace the in-memory history in `dm_agent.py` with Redis or a database.
- Set `APP_SECRET` so webhook signatures are verified.
- Keep `confirm=false` publishing until you trust the content quality.
- Add rate limiting and logging of handoffs/leads (currently printed to console).
- Exchange the short-lived token for a long-lived one and refresh it every ~60 days.
