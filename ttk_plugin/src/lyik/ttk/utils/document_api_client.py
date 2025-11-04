import requests
from typing import Dict, Any, Optional


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
            "TTK-Token": ttk_token,
        }

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
        try:
            response = requests.post(
                url, json=payload, headers=self.headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {e}") from e
        except ValueError:
            raise ValueError("Failed to parse JSON response from API")

        if "responseData" not in data:
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
        payload = {"orderId": order_id, "documentId": document_id}
        return self._post(endpoint, payload)
