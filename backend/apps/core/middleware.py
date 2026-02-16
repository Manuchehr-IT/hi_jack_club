import logging

logger = logging.getLogger("apps.core.middleware")

class DebugHeadersMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		auth_header = request.META.get("HTTP_AUTHORIZATION")
		logger.debug(f"Incoming request: {request.method} {request.path} | Authorization: {auth_header}")
		response = self.get_response(request)
		logger.debug(f"Response status: {response.status_code} for {request.method} {request.path}")
		return response
