"""
Views for the password checker app.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.views.decorators.cache import never_cache
import json
import math
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Security constants
MAX_PASSWORD_LENGTH = 128  # Maximum reasonable password length
MIN_PASSWORD_LENGTH = 1    # Minimum to analyze
MAX_REQUESTS_PER_MINUTE = 60  # Rate limit per IP


def validate_and_sanitize_password(password):
    """
    Validate and sanitize password input.
    
    Args:
        password (str): The password to validate
        
    Returns:
        tuple: (is_valid, error_message, sanitized_password)
    """
    # Check if password is string
    if not isinstance(password, str):
        return False, "Password must be a string", None
    
    # Check length constraints
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, "Password cannot be empty", None
    
    if len(password) > MAX_PASSWORD_LENGTH:
        return False, f"Password exceeds maximum length of {MAX_PASSWORD_LENGTH} characters", None
    
    # Check for null bytes (potential injection attempts)
    if '\x00' in password:
        return False, "Invalid characters in password", None
    
    # Sanitize: Remove any potential control characters except common ones
    # Allow printable ASCII, extended ASCII, and common Unicode characters
    # This preserves legitimate special characters while blocking control chars
    sanitized = ''.join(char for char in password if ord(char) >= 32 or char in '\t\n\r')
    
    return True, None, sanitized


def check_rate_limit(request):
    """
    Implement rate limiting per IP address.
    
    Args:
        request: Django request object
        
    Returns:
        tuple: (is_allowed, remaining_requests)
    """
    # Get client IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    
    # Create cache key
    cache_key = f'password_check_rate_limit_{ip}'
    
    # Get current request count
    request_count = cache.get(cache_key, 0)
    
    # Check if limit exceeded
    if request_count >= MAX_REQUESTS_PER_MINUTE:
        return False, 0
    
    # Increment counter
    cache.set(cache_key, request_count + 1, 60)  # Expire in 60 seconds
    
    remaining = MAX_REQUESTS_PER_MINUTE - request_count - 1
    return True, remaining


def estimate_password(password):
    """
    Estimate password strength based on entropy and character diversity.
    
    Args:
        password (str): The password to analyze
        
    Returns:
        dict: Contains entropy, time to crack, strength rating, and feedback
    """
    # Step 1: Determine character pool
    pool = 0
    feedback = []
    
    if any(c.islower() for c in password):
        pool += 26
    else:
        feedback.append("Add lowercase letters")
        
    if any(c.isupper() for c in password):
        pool += 26
    else:
        feedback.append("Add uppercase letters")
        
    if any(c.isdigit() for c in password):
        pool += 10
    else:
        feedback.append("Add numbers")
        
    if any(not c.isalnum() for c in password):
        pool += 32
    else:
        feedback.append("Add symbols")
        
    L = len(password)
    if L < 8:
        feedback.append("Use at least 8 characters")
    
    # Step 2: Calculate entropy
    entropy = L * math.log2(pool) if pool else 0
    
    # Step 3: Convert entropy → guesses → seconds
    guesses = 2 ** entropy
    guesses_per_second = 10_000_000_000  # 10 billion guesses/sec
    time_sec = guesses / guesses_per_second
    
   # Step 4: Convert seconds → human-readable time
    if time_sec < 60:
        time_str = f"{time_sec:.1f} seconds"
    elif time_sec < 3600:
        time_str = f"{time_sec/60:.1f} minutes"
    elif time_sec < 86400:
        time_str = f"{time_sec/3600:.1f} hours"
    elif time_sec < 31536000:
        time_str = f"{time_sec/86400:.1f} days"
    elif time_sec < 3153600000:  # ~100 years
        time_str = f"{time_sec/31536000:.1f} years"
    else:
        time_str = "Centuries+"

    # Step 5: Strength label
    if entropy < 28:
        strength = "Very Weak"
    elif entropy < 36:
        strength = "Weak"
    elif entropy < 60:
        strength = "Medium"
    elif entropy < 80:
        strength = "Strong"
    else:
        strength = "Very Strong"
    
    return {
        "entropy_bits": round(entropy, 2),
        "time_to_crack": time_str,
        "strength": strength,
        "feedback": feedback,
        "character_pool": pool,
        "password_length": L
    }


@ensure_csrf_cookie
@never_cache
def index(request):
    """
    Render the main password checker page.
    Ensures CSRF token is set for API calls.
    """
    return render(request, 'index.html')


@require_http_methods(["POST"])
@never_cache
def check_password(request):
    """
    API endpoint to check password strength with comprehensive security measures.
    
    Security features:
    - Input validation and sanitization
    - Rate limiting per IP
    - CSRF protection
    - Request size limits
    - No password logging
    - Proper error handling
    
    Expects JSON POST data with 'password' field.
    Returns JSON response with password analysis.
    """
    try:
        # Check rate limit
        is_allowed, remaining = check_rate_limit(request)
        if not is_allowed:
            logger.warning(f"Rate limit exceeded for IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
            return JsonResponse({
                'error': 'Rate limit exceeded. Please try again later.',
                'rate_limit_exceeded': True
            }, status=429)
        
        # Check request size (prevent DoS attacks)
        if len(request.body) > 1024 * 10:  # 10KB max
            logger.warning(f"Request body too large from IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
            return JsonResponse({
                'error': 'Request body too large'
            }, status=413)
        
        # Parse JSON data from request
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        
        # Extract password
        password = data.get('password')
        
        # Validate that password field exists
        if password is None:
            return JsonResponse({
                'error': 'Password field is required'
            }, status=400)
        
        # Validate and sanitize password
        is_valid, error_message, sanitized_password = validate_and_sanitize_password(password)
        
        if not is_valid:
            return JsonResponse({
                'error': error_message
            }, status=400)
        
        # Analyze password (using sanitized version)
        result = estimate_password(sanitized_password)
        
        # Add rate limit info to response headers
        response = JsonResponse(result)
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Limit'] = str(MAX_REQUESTS_PER_MINUTE)
        
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        
        return response
        
    except Exception as e:
        # Log error without exposing password
        logger.error(f"Unexpected error in check_password: {type(e).__name__}")
        return JsonResponse({
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)
