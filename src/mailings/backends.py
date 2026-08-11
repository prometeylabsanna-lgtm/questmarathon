import logging

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)


class ResendEmailBackend(BaseEmailBackend):
    """Send email via Resend API. Requires RESEND_API_KEY in settings."""

    def send_messages(self, email_messages):
        if not email_messages:
            return 0
        api_key = getattr(settings, "RESEND_API_KEY", "")
        if not api_key:
            logger.error("RESEND_API_KEY is empty — emails not sent")
            if self.fail_silently:
                return 0
            raise RuntimeError("RESEND_API_KEY is not configured")

        import resend

        resend.api_key = api_key
        sent = 0
        for message in email_messages:
            try:
                payload = {
                    "from": message.from_email or settings.DEFAULT_FROM_EMAIL,
                    "to": list(message.to),
                    "subject": message.subject,
                }
                if message.body:
                    payload["text"] = message.body
                if getattr(message, "alternatives", None):
                    for content, mimetype in message.alternatives:
                        if mimetype == "text/html":
                            payload["html"] = content
                            break
                resend.Emails.send(payload)
                sent += 1
            except Exception:
                logger.exception("Resend send failed")
                if not self.fail_silently:
                    raise
        return sent
