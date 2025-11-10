"""
Tests for health check endpoint
"""
from django.test import TestCase, Client
from django.urls import reverse
import json


class HealthCheckTestCase(TestCase):
    """Test cases for the health check endpoint"""

    def setUp(self):
        """Set up test client"""
        self.client = Client()
        self.health_url = reverse('health_check')

    def test_health_check_endpoint_exists(self):
        """Test that /health/ endpoint is accessible"""
        response = self.client.get(self.health_url)
        self.assertIn(response.status_code, [200, 503])

    def test_health_check_returns_json(self):
        """Test that health check returns JSON response"""
        response = self.client.get(self.health_url)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_health_check_returns_200_when_healthy(self):
        """Test that health check returns 200 status when database is connected"""
        response = self.client.get(self.health_url)
        self.assertEqual(response.status_code, 200)

        # Parse JSON response
        data = json.loads(response.content)

        # Verify response structure
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('database', data)
        self.assertIn('service', data)

        # Verify status is healthy
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['database'], 'connected')
        self.assertEqual(data['service'], 'neulbom')

    def test_health_check_includes_timestamp(self):
        """Test that health check response includes a timestamp"""
        response = self.client.get(self.health_url)
        data = json.loads(response.content)

        self.assertIn('timestamp', data)
        self.assertIsNotNone(data['timestamp'])

    def test_health_check_response_time(self):
        """Test that health check responds within 3 seconds (NFR002 requirement)"""
        import time

        start_time = time.time()
        response = self.client.get(self.health_url)
        end_time = time.time()

        response_time = end_time - start_time

        # Should respond in less than 3 seconds
        self.assertLess(response_time, 3.0,
                        f"Health check took {response_time:.2f}s, exceeds 3s requirement")

    def test_health_check_database_connectivity(self):
        """Test that health check verifies database connectivity"""
        response = self.client.get(self.health_url)
        data = json.loads(response.content)

        # Database should be connected in test environment
        self.assertEqual(data['database'], 'connected')
