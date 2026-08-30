from django.urls import path
from moderation.views import PredictView, StatsView, BenchmarkView, slack_events

urlpatterns = [
    path("predict/", PredictView.as_view(), name="predict"),
    path("stats/", StatsView.as_view(), name="stats"),
    path("benchmark/", BenchmarkView.as_view(), name="benchmark"),
    path("slack/events", slack_events),
]
