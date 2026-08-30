from django.core.management.base import BaseCommand
from moderation.inference import ensure_model_downloaded


class Command(BaseCommand):
    help = "Pre-download the model and thresholds from Hugging Face Hub at build time"

    def handle(self, *args, **options):
        self.stdout.write("Downloading model from Hugging Face Hub...")
        ensure_model_downloaded()
        self.stdout.write(self.style.SUCCESS("Model download complete."))
