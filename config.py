import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")

IG_USER_ID = os.getenv("IG_USER_ID", "")            # Instagram Business/Creator account ID
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "")  # Long-lived token
GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v21.0")
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "change-me")  # for webhook verification
APP_SECRET = os.getenv("APP_SECRET", "")               # to verify webhook signatures

BRAND_NAME = os.getenv("BRAND_NAME", "My Brand")
BRAND_VOICE = os.getenv(
    "BRAND_VOICE",
    "Friendly, concise, helpful. Uses light emoji. Never pushy.",
)
BUSINESS_INFO = os.getenv(
    "BUSINESS_INFO",
    "Describe your products, prices, hours, shipping, and policies here.",
)
HUMAN_HANDOFF_CONTACT = os.getenv("HUMAN_HANDOFF_CONTACT", "our team will reply soon")
