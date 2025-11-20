import os
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Reuse the same verbose flag (or allow separate override)
_VERBOSE_LOG_ENV = os.getenv("DOCUMENT_GEN_API_VERBOSE_LOGS", "true").lower()
VERBOSE_LOG_ENABLED = _VERBOSE_LOG_ENV in ("1", "true", "yes", "on")


def _debug_log(message: str, *args, **kwargs) -> None:
    if VERBOSE_LOG_ENABLED:
        logger.debug(message, *args, **kwargs)


def _log_exception(message: str, exc: Exception) -> None:
    if VERBOSE_LOG_ENABLED:
        logger.exception(
            "%s | type=%s, repr=%r",
            message,
            type(exc).__name__,
            exc,
        )
    else:
        logger.error("%s: %s", message, exc)


class DocumentAPIClient:
    """
    Utility class to interact with TTK Document APIs.

    This class supports:
      1. Fetching the list of documents for a given order ID.
      2. Fetching detailed document information (including base64 content)
         for a specific document ID under an order.
    """

    def __init__(self, base_url: str, ttk_token: str):
        """
        Initialize the DocumentAPIClient.

        Args:
            base_url (str): Base URL of the API.
            ttk_token (str): Authentication token (TTK Token) to include in headers.
        """
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ttk_token}",
        }
        _debug_log(
            "DocumentAPIClient initialized | base_url=%s, headers_keys=%s",
            self.base_url,
            list(self.headers.keys()),
        )

    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to perform POST requests and handle errors.

        Args:
            endpoint (str): API endpoint path.
            payload (Dict[str, Any]): Request body.

        Returns:
            Dict[str, Any]: Parsed JSON response from API.

        Raises:
            requests.exceptions.RequestException: If request fails.
            ValueError: If response cannot be parsed or has unexpected format.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        _debug_log(
            "DocumentAPIClient._post | url=%s, payload_keys=%s",
            url,
            list(payload.keys()),
        )

        try:
            response = requests.post(
                url, json=payload, headers=self.headers, timeout=30
            )
            _debug_log(
                "DocumentAPIClient._post | status_code=%s",
                response.status_code,
            )
            response.raise_for_status()
            data = response.json()
            _debug_log(
                "DocumentAPIClient._post | response_json_keys=%s",
                list(data.keys()) if isinstance(data, dict) else None,
            )
        except requests.exceptions.RequestException as e:
            _log_exception("HTTP request failed in DocumentAPIClient._post", e)
            raise RuntimeError(f"HTTP request failed: {e}") from e
        except ValueError as e:
            # Could be either response.json() or our own check.
            _log_exception("Failed to parse JSON response from API", e)
            raise ValueError("Failed to parse JSON response from API") from e

        if "responseData" not in data:
            # This will be what you'd see if the API changed shape.
            logger.error(
                "Unexpected response: 'responseData' missing | data_keys=%s",
                list(data.keys()) if isinstance(data, dict) else None,
            )
            raise ValueError("Unexpected response: 'responseData' missing")

        return data

    def get_document_list(self, endpoint: str, order_id: str) -> Dict[str, Any]:
        """
        Fetch the list of documents for a given order ID.

        Args:
            endpoint (str): API endpoint.
            order_id (str): Order ID to fetch document list for.

        Returns:
            Dict[str, Any]: API response containing document list.
        """
        _debug_log(
            "DocumentAPIClient.get_document_list | endpoint=%s, order_id=%s",
            endpoint,
            order_id,
        )
        payload = {"orderId": order_id}
        return self._post(endpoint, payload)

    def get_document_by_id(
        self, endpoint: str, order_id: str, document_id: str
    ) -> Dict[str, Any]:
        """
        Fetch detailed document information for a specific document ID.

        Args:
            endpoint (str): API endpoint.
            order_id (str): Order ID associated with the document.
            document_id (str): Document ID to fetch details for.

        Returns:
            Dict[str, Any]: API response containing document detail and the actual document in base64.
        """
        _debug_log(
            "DocumentAPIClient.get_document_by_id | endpoint=%s, order_id=%s, document_id=%s",
            endpoint,
            order_id,
            document_id,
        )
        payload = {"orderId": order_id, "documentId": document_id}
        return self._post(endpoint, payload)
