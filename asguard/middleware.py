# yourapp/middleware.py

import logging

logger = logging.getLogger("user_activity")

class UvicornUserLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Optional: skip static/media paths
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return response

        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else "Anonymous"
        method = request.method
        path = request.get_full_path()
        status = response.status_code
        ip = request.META.get('REMOTE_ADDR', '-')

        # Log the custom access message
        logger.info(f"[ACCESS] {ip} - {method} {path} ({status}) | user={username}")

        return response
