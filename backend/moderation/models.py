from django.db import models


class FlaggedMessage(models.Model):
    ACTION_CHOICES = [
        ("none", "None"),
        ("flag", "Flagged"),
        ("flag_high", "Flagged (High Confidence)"),
    ]

    slack_user_id = models.CharField(max_length=64)
    slack_channel_id = models.CharField(max_length=64)
    message_ts = models.CharField(max_length=32)
    text = models.TextField()
    toxic = models.FloatField(default=0.0)
    severe_toxic = models.FloatField(default=0.0)
    obscene = models.FloatField(default=0.0)
    threat = models.FloatField(default=0.0)
    insult = models.FloatField(default=0.0)
    identity_hate = models.FloatField(default=0.0)
    max_score = models.FloatField(default=0.0)
    action_taken = models.CharField(
        max_length=16, choices=ACTION_CHOICES, default="none"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["slack_user_id"]),
        ]


class UserHistory(models.Model):
    slack_user_id = models.CharField(max_length=64, unique=True)
    flagged_count = models.IntegerField(default=0)
    high_confidence_count = models.IntegerField(default=0)
    last_flagged_at = models.DateTimeField(null=True, blank=True)
