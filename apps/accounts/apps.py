from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'Accounts'

    def ready(self):
        # Warm up Firebase Admin in production-like environments to reduce first-login latency.
        if not (os.environ.get('FIREBASE_CREDENTIALS_JSON') or os.environ.get('FIREBASE_CREDENTIALS_PATH')):
            return

        try:
            from .authentication import initialize_firebase
            initialize_firebase()
        except Exception as exc:
            logger.warning("Firebase pre-initialization skipped: %s", exc)
