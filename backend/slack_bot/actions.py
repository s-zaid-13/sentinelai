def warn_user(client, user_id, channel_id, scores):
    dm = client.conversations_open(users=[user_id])
    dm_channel = dm["channel"]["id"]
    client.chat_postMessage(
        channel=dm_channel,
        text=f"Your recent message in <#{channel_id}> was flagged for a policy violation. Please review workplace communication guidelines.",
    )


def alert_admin(client, admin_channel_id, user_id, channel_id, text, scores):
    if not admin_channel_id:
        return
    top_label = max(scores, key=scores.get)
    client.chat_postMessage(
        channel=admin_channel_id,
        text=(
            f"Flagged message from <@{user_id}> in <#{channel_id}>\n"
            f"Top category: {top_label} ({scores[top_label]:.2f})\n"
            f"Text: {text}"
        ),
    )
