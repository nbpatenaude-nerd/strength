import threading
import requests
import logging
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from wger.manager.models import WorkoutSession
from wger.nutrition.models import LogItem

logger = logging.getLogger(__name__)

def dispatch_webhook(payload):
    url = getattr(settings, "JOURNEY_ENDURANCE_WEBHOOK_URL", None)
    secret = getattr(settings, "JOURNEY_ENDURANCE_WEBHOOK_SECRET", "")
    
    if not url:
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {secret}"
    }

    try:
        requests.post(url, json=payload, headers=headers, timeout=5)
        logger.info(f"Successfully dispatched webhook to {url}")
    except Exception as e:
        logger.error(f"Failed to dispatch webhook to {url}: {e}")

def run_webhook_in_background(payload):
    thread = threading.Thread(target=dispatch_webhook, args=(payload,))
    thread.daemon = True
    thread.start()

@receiver(post_save, sender=WorkoutSession)
def workout_session_webhook(sender, instance, created, **kwargs):
    payload = {
        "event": "workout_session_saved",
        "user_id": instance.user.id,
        "session_id": instance.id,
        "date": str(instance.date),
        "notes": instance.notes
    }
    run_webhook_in_background(payload)

@receiver(post_save, sender=LogItem)
def nutrition_log_webhook(sender, instance, created, **kwargs):
    payload = {
        "event": "nutrition_log_saved",
        "user_id": instance.user.id,
        "log_id": instance.id,
        "date": str(instance.date),
        "amount": float(instance.amount) if instance.amount else 0,
        "ingredient_id": instance.ingredient.id if instance.ingredient else None
    }
    run_webhook_in_background(payload)
