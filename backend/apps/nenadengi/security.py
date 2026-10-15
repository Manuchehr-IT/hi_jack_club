import hashlib
import hmac

from django.conf import settings


def verify_webhook_signature(timestamp: str, raw_body: bytes, signature: str) -> bool:
	if not timestamp or not signature or not settings.NENADENGI_WEBHOOK_SECRET:
		return False

	expected = hmac.new(
		settings.NENADENGI_WEBHOOK_SECRET.encode(),
		f"{timestamp}.".encode() + raw_body,
		hashlib.sha256,
	).hexdigest()

	return hmac.compare_digest(expected, signature)
