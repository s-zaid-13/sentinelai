import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sentinelai_backend.settings")
django.setup()

import requests
from slack_bolt import App
from django.conf import settings
from slack_bot.actions import warn_user, alert_admin

app = App(
    token=settings.SLACK_BOT_TOKEN,
    signing_secret=settings.SLACK_SIGNING_SECRET,
    process_before_response=True,
)


def ack_immediately(ack):
    ack()


def process_message_event(body, client):
    event = body.get("event", {})

    if event.get("subtype") is not None:
        return
    if event.get("bot_id"):
        return

    text = event.get("text", "")
    user_id = event.get("user")
    channel_id = event.get("channel")
    message_ts = event.get("ts")

    if not text or not user_id:
        return

    try:
        response = requests.post(
            f"{settings.DJANGO_API_URL}/predict/",
            json={
                "slack_user_id": user_id,
                "slack_channel_id": channel_id,
                "message_ts": message_ts,
                "text": text,
            },
            timeout=90,
        )
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as e:
        app.logger.error(f"Predict call failed: {e}")
        return

    action = result["action"]
    scores = result["scores"]

    if action == "flag":
        alert_admin(
            client, settings.SLACK_ADMIN_CHANNEL_ID, user_id, channel_id, text, scores
        )
    elif action == "flag_high":
        warn_user(client, user_id, channel_id, scores)
        alert_admin(
            client, settings.SLACK_ADMIN_CHANNEL_ID, user_id, channel_id, text, scores
        )


app.event("message")(ack=ack_immediately, lazy=[process_message_event])
