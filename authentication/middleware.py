"""
Middleware for enforcing authentication on protected routes.
"""

from django.shortcuts import redirect
from django.urls import reverse
import re
import logging

logger = logging.getLogger(__name__)


class AuthenticationEnforcementMiddleware:
    """
    Middleware that enforces authentication for all routes except public ones.

    Public routes (accessible without authentication):
    - / (landing page)
    - /accounts/login/
    - /accounts/logout/
    - /static/*
    - /media/*
    - /health/ (health check endpoint)
    """

    PUBLIC_URLS = [
        r'^/$',  # Landing page
        r'^/accounts/login/',
        r'^/accounts/logout/',
        r'^/static/',
        r'^/media/',
        r'^/health/',  # Health check endpoint
    ]

    def __init__(self, get_response):
        """
        Initialize middleware.

        Args:
            get_response: Next middleware or view in the chain
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Process request and enforce authentication.

        Args:
            request: HTTP request object

        Returns:
            HTTP response (either redirect to login or response from next handler)
        """
        if not request.user.is_authenticated:
            # Check if current URL is public
            path = request.path_info
            is_public = any(re.match(pattern, path) for pattern in self.PUBLIC_URLS)

            if not is_public:
                logger.info(
                    f"Unauthenticated access attempt to protected route: {path}"
                )
                return redirect('/accounts/login/?next=' + path)

        response = self.get_response(request)
        return response
