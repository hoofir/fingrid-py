import logging
from typing import Any

import requests
from requests.exceptions import HTTPError, RequestException

# ---------------------------------------------------------

logging.basicConfig(
    force=True,
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------


class APIClient:
    def __init__(self, headers: dict):
        self.session = requests.Session()
        self.session.headers.update(headers)
        self._logger = logging.getLogger(__name__)

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self) -> None:
        self.close()

    def close(self) -> None:
        self.session.close()

    def get(self, url: str, params: dict | None = None) -> Any:
        """
        Make a GET request to the specified endpoint
        with required and optional parameters.
        Args:
            url (str): The API's endpoint path to call.
            params (dict, Optional): Dictionary of parameters. Default None
        Returns:
            dict: The JSON response from the API.
        """
        try:
            response = self.session.get(url=url, params=params)
            response.raise_for_status()  # Status codes (4xx, 5xx)
            return response.json()  # .text or .content depending on the API response
        except HTTPError as e:
            status = e.response.status_code if e.response else "unknown"
            logger.error(f"HTTP error code {status}: {e}")
        except RequestException as e:
            logger.error(f"Request error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        return None
