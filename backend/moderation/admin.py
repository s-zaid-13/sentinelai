from django.contrib import admin
from moderation.models import FlaggedMessage, UserHistory

admin.site.register(FlaggedMessage)
admin.site.register(UserHistory)
