"""
Custom security middleware for the password checker app.
"""
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware:
    """
    Add additional security headers to all responses.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        return response


class RequestLoggingMiddleware:
    """
    Log suspicious requests without logging sensitive data.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log suspicious patterns (without logging actual passwords)
        if request.path == '/api/check/':
            # Check for suspicious request patterns
            if request.method != 'POST':
                logger.warning(
                    f"Non-POST request to /api/check/ from {request.META.get('REMOTE_ADDR', 'unknown')}"
                )
            
            # Check Content-Type
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'application/json' not in content_type:
                logger.warning(
                    f"Invalid Content-Type for /api/check/: {content_type} "
                    f"from {request.META.get('REMOTE_ADDR', 'unknown')}"
                )
        
        response = self.get_response(request)
        return response
