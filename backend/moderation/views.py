from django.utils import timezone
from django.db.models import Count, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from moderation.serializers import PredictRequestSerializer
from moderation.models import FlaggedMessage, UserHistory
from moderation.inference import predict, get_thresholds, apply_thresholds
from django.conf import settings
import json

from django.views.decorators.csrf import csrf_exempt
from slack_bolt.adapter.django import SlackRequestHandler
from slack_bot.bolt_app import app

handler = SlackRequestHandler(app)


class PredictView(APIView):
    def post(self, request):
        serializer = PredictRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        scores = predict(data["text"])
        flags = apply_thresholds(scores)
        flagged_labels = [label for label, is_flagged in flags.items() if is_flagged]

        if not flagged_labels:
            action = "none"
        else:
            severe_labels = set(settings.HIGH_CONFIDENCE_LABELS)
            is_high = any(label in severe_labels for label in flagged_labels)
            action = "flag_high" if is_high else "flag"

        record = FlaggedMessage.objects.create(
            slack_user_id=data["slack_user_id"],
            slack_channel_id=data["slack_channel_id"],
            message_ts=data["message_ts"],
            text=data["text"],
            action_taken=action,
            max_score=max(scores.values()),
            **scores,
        )

        if action in ("flag", "flag_high"):
            history, _ = UserHistory.objects.get_or_create(
                slack_user_id=data["slack_user_id"]
            )
            history.flagged_count += 1
            if action == "flag_high":
                history.high_confidence_count += 1
            history.last_flagged_at = timezone.now()
            history.save()

        return Response(
            {
                "id": record.id,
                "scores": scores,
                "flagged_categories": flagged_labels,
                "action": action,
            },
            status=status.HTTP_201_CREATED,
        )


class StatsView(APIView):
    def get(self, request):
        today = timezone.now().date()

        total_scanned = FlaggedMessage.objects.count()
        scanned_today = FlaggedMessage.objects.filter(created_at__date=today).count()
        flagged_today = FlaggedMessage.objects.filter(
            created_at__date=today, action_taken__in=["flag", "flag_high"]
        ).count()

        thresholds = get_thresholds()
        category_breakdown = {
            label: FlaggedMessage.objects.filter(
                **{f"{label}__gte": thresholds.get(label, 0.5)}
            ).count()
            for label in settings.LABEL_COLUMNS
        }

        trend = (
            FlaggedMessage.objects.filter(action_taken__in=["flag", "flag_high"])
            .extra(select={"day": "date(created_at)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        repeat_offenders = (
            UserHistory.objects.filter(flagged_count__gt=1)
            .order_by("-flagged_count")
            .values("slack_user_id", "flagged_count", "high_confidence_count")[:10]
        )

        return Response(
            {
                "total_scanned": total_scanned,
                "scanned_today": scanned_today,
                "flagged_today": flagged_today,
                "category_breakdown": category_breakdown,
                "trend": list(trend),
                "repeat_offenders": list(repeat_offenders),
            }
        )


class BenchmarkView(APIView):
    def get(self, request):
        try:
            with open(settings.BENCHMARK_REPORT_PATH) as f:
                data = json.load(f)
            return Response(data)
        except FileNotFoundError:
            return Response({"available": False}, status=status.HTTP_200_OK)


@csrf_exempt
def slack_events(request):
    return handler.handle(request)
