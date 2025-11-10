"""
ZEP API Client for space creation and permission management

This module provides an interface to interact with ZEP's API
for creating spaces and managing permissions.
"""

import requests
import logging
from django.conf import settings
from typing import Dict, List, Optional
import time

logger = logging.getLogger(__name__)


class ZEPAPIError(Exception):
    """Custom exception for ZEP API errors"""
    pass


class ZEPClient:
    """
    Client for interacting with ZEP API

    Handles authentication, rate limiting, and retry logic
    """

    def __init__(self):
        """
        Initialize ZEP API client

        Requires environment variables:
        - ZEP_API_KEY: API authentication key
        - ZEP_API_URL: Base URL for ZEP API (default: https://api.zep.us/v1)
        """
        self.api_key = getattr(settings, 'ZEP_API_KEY', None)
        self.api_url = getattr(settings, 'ZEP_API_URL', 'https://api.zep.us/v1')
        self.timeout = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 2  # seconds

        if not self.api_key:
            logger.warning("ZEP_API_KEY not configured. ZEP API calls will fail.")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers for API requests

        Returns:
            dict: Headers including authentication
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        retry_count: int = 0
    ) -> Dict:
        """
        Make HTTP request to ZEP API with retry logic

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request payload (for POST/PUT)
            retry_count: Current retry attempt number

        Returns:
            dict: API response data

        Raises:
            ZEPAPIError: If API request fails after retries
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"

        try:
            logger.debug(f"Making {method} request to {url}")

            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                timeout=self.timeout
            )

            # Log response for debugging
            logger.debug(f"Response status: {response.status_code}")

            # Handle rate limiting (429)
            if response.status_code == 429:
                if retry_count < self.max_retries:
                    wait_time = self.retry_delay * (retry_count + 1)
                    logger.warning(f"Rate limited. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    return self._make_request(method, endpoint, data, retry_count + 1)
                else:
                    raise ZEPAPIError(f"Rate limit exceeded. Max retries reached.")

            # Handle server errors (5xx) with retry
            if 500 <= response.status_code < 600:
                if retry_count < self.max_retries:
                    wait_time = self.retry_delay * (retry_count + 1)
                    logger.warning(f"Server error {response.status_code}. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    return self._make_request(method, endpoint, data, retry_count + 1)

            # Raise exception for error status codes
            response.raise_for_status()

            return response.json()

        except requests.exceptions.Timeout:
            if retry_count < self.max_retries:
                logger.warning(f"Request timeout. Retrying... (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
                return self._make_request(method, endpoint, data, retry_count + 1)
            raise ZEPAPIError(f"Request timeout after {self.max_retries} retries")

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            if retry_count < self.max_retries:
                logger.warning(f"Retrying... (attempt {retry_count + 1}/{self.max_retries})")
                time.sleep(self.retry_delay)
                return self._make_request(method, endpoint, data, retry_count + 1)
            raise ZEPAPIError(f"Request failed after {self.max_retries} retries: {e}")

    def create_space(
        self,
        name: str,
        owner_email: str,
        template_id: Optional[str] = None,
        description: str = ""
    ) -> Dict:
        """
        Create a new ZEP space

        Args:
            name: Space name
            owner_email: Email of the space owner
            template_id: Optional template ID to use for space creation
            description: Space description

        Returns:
            dict: Created space information including space_id and url

        Raises:
            ZEPAPIError: If space creation fails
        """
        logger.info(f"Creating ZEP space: {name} for {owner_email}")

        payload = {
            'name': name,
            'owner_email': owner_email,
            'description': description,
        }

        if template_id:
            payload['template_id'] = template_id

        try:
            response = self._make_request('POST', '/spaces', data=payload)
            logger.info(f"Space created successfully: {response.get('space_id')}")
            return response

        except ZEPAPIError as e:
            logger.error(f"Failed to create space: {e}")
            raise

    def set_space_permissions(
        self,
        space_id: str,
        owner_email: str,
        staff_emails: Optional[List[str]] = None
    ) -> Dict:
        """
        Set permissions for a ZEP space

        Args:
            space_id: ZEP space ID
            owner_email: Email of the owner (full access)
            staff_emails: List of staff member emails (edit access)

        Returns:
            dict: Updated permission information

        Raises:
            ZEPAPIError: If permission update fails
        """
        logger.info(f"Setting permissions for space {space_id}")

        payload = {
            'owner': owner_email,
            'staff': staff_emails or []
        }

        try:
            response = self._make_request(
                'PUT',
                f'/spaces/{space_id}/permissions',
                data=payload
            )
            logger.info(f"Permissions updated successfully for space {space_id}")
            return response

        except ZEPAPIError as e:
            logger.error(f"Failed to set permissions: {e}")
            raise

    def get_space_info(self, space_id: str) -> Dict:
        """
        Get information about a ZEP space

        Args:
            space_id: ZEP space ID

        Returns:
            dict: Space information

        Raises:
            ZEPAPIError: If request fails
        """
        logger.info(f"Getting info for space {space_id}")

        try:
            response = self._make_request('GET', f'/spaces/{space_id}')
            return response

        except ZEPAPIError as e:
            logger.error(f"Failed to get space info: {e}")
            raise

    def delete_space(self, space_id: str) -> bool:
        """
        Delete a ZEP space

        Args:
            space_id: ZEP space ID

        Returns:
            bool: True if deletion successful

        Raises:
            ZEPAPIError: If deletion fails
        """
        logger.info(f"Deleting space {space_id}")

        try:
            self._make_request('DELETE', f'/spaces/{space_id}')
            logger.info(f"Space {space_id} deleted successfully")
            return True

        except ZEPAPIError as e:
            logger.error(f"Failed to delete space: {e}")
            raise


# Singleton instance
_client = None


def get_zep_client() -> ZEPClient:
    """
    Get singleton ZEP client instance

    Returns:
        ZEPClient: Shared ZEP client instance
    """
    global _client
    if _client is None:
        _client = ZEPClient()
    return _client
