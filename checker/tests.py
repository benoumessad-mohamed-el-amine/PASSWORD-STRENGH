"""
Tests for password checker app including security tests.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
import json


class PasswordCheckerTests(TestCase):
    """Test cases for password strength checker."""
    
    def setUp(self):
        """Set up test client and clear cache."""
        self.client = Client()
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_index_page_loads(self):
        """Test that the main page loads successfully."""
        response = self.client.get(reverse('checker:index'))
        self.assertEqual(response.status_code, 200)
        # Check that CSRF cookie is set
        self.assertIn('csrftoken', response.cookies)
    
    def test_weak_password(self):
        """Test detection of weak password."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 'password'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('strength', data)
        self.assertIn('Weak', data['strength'])
    
    def test_strong_password(self):
        """Test detection of strong password."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 'MyStr0ng!P@ssw0rd#2024'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('strength', data)
        self.assertIn('Strong', data['strength'])
    
    def test_empty_password(self):
        """Test handling of empty password."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_password_feedback(self):
        """Test that feedback is provided for weak passwords."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 'abc'}),
            content_type='application/json'
        )
        data = response.json()
        self.assertIn('feedback', data)
        self.assertTrue(len(data['feedback']) > 0)


class SecurityTests(TestCase):
    """Security-specific test cases."""
    
    def setUp(self):
        """Set up test client and clear cache."""
        self.client = Client(enforce_csrf_checks=True)
        cache.clear()
    
    def tearDown(self):
        """Clean up after tests."""
        cache.clear()
    
    def test_csrf_protection(self):
        """Test that CSRF protection is enabled."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 'test123'}),
            content_type='application/json'
        )
        # Should fail without CSRF token
        self.assertEqual(response.status_code, 403)
    
    def test_csrf_with_token(self):
        """Test that requests with CSRF token succeed."""
        # Get CSRF token
        self.client.get(reverse('checker:index'))
        
        # Make request with token
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 'test123'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_rate_limiting(self):
        """Test that rate limiting works."""
        # Clear cache to start fresh
        cache.clear()
        
        # Make 60 requests (should all succeed)
        for i in range(60):
            response = self.client.post(
                reverse('checker:check_password'),
                data=json.dumps({'password': 'test'}),
                content_type='application/json'
            )
            if i < 59:
                self.assertEqual(response.status_code, 200)
        
        # 61st request should be rate limited
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 'test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 429)
        data = response.json()
        self.assertIn('rate_limit_exceeded', data)
    
    def test_max_password_length(self):
        """Test that passwords exceeding max length are rejected."""
        long_password = 'a' * 200  # Exceeds 128 char limit
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': long_password}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('maximum length', data['error'])
    
    def test_null_byte_injection(self):
        """Test that null byte injection is blocked."""
        malicious_password = 'test\x00injection'
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': malicious_password}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_request_too_large(self):
        """Test that oversized requests are rejected."""
        # Create a request larger than 10KB
        huge_data = 'x' * (11 * 1024)  # 11KB
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': huge_data}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 413)
    
    def test_invalid_json(self):
        """Test that invalid JSON is rejected."""
        response = self.client.post(
            reverse('checker:check_password'),
            data='invalid json{',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('Invalid JSON', data['error'])
    
    def test_missing_password_field(self):
        """Test that missing password field is rejected."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'notpassword': 'test'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('required', data['error'])
    
    def test_non_string_password(self):
        """Test that non-string passwords are rejected."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 12345}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
    
    def test_security_headers(self):
        """Test that security headers are present."""
        response = self.client.get(reverse('checker:index'))
        
        # Check for security headers
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertIn('X-XSS-Protection', response)
        self.assertIn('Content-Security-Policy', response)
    
    def test_rate_limit_headers(self):
        """Test that rate limit headers are present."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 'test'}),
            content_type='application/json'
        )
        
        # Check for rate limit headers
        self.assertIn('X-RateLimit-Remaining', response)
        self.assertIn('X-RateLimit-Limit', response)
    
    def test_get_request_not_allowed(self):
        """Test that GET requests are not allowed for API."""
        response = self.client.get(reverse('checker:check_password'))
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
    
    def test_cache_control_headers(self):
        """Test that API responses are not cached."""
        response = self.client.post(
            reverse('checker:check_password'),
            data=json.dumps({'password': 'test'}),
            content_type='application/json'
        )
        
        # Check that caching is disabled
        self.assertIn('Cache-Control', response)
        cache_control = response['Cache-Control']
        self.assertIn('no-cache', cache_control.lower())

