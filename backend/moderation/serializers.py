from rest_framework import serializers
from moderation.models import FlaggedMessage, UserHistory


class PredictRequestSerializer(serializers.Serializer):
    slack_user_id = serializers.CharField()
    slack_channel_id = serializers.CharField()
    message_ts = serializers.CharField()
    text = serializers.CharField()


class FlaggedMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlaggedMessage
        fields = "__all__"


class UserHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserHistory
        fields = "__all__"
