import logging
import os
import time
from collections import deque

from .client import APIClient
from .utils import load_yaml

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yml")

# ---------------------------------------------------------

logging.basicConfig(
    force=True,
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------


class Endpoint:
    """
    Abstract base class for API endpoints.
    Args:
        api_key (str): Personal API key for authentication.
        **params: Endpoint-specific kwargs as Get method's parameters.
    """

    _request_timestamps = deque()  # Shared tracker for all instances

    def __init__(self, api_key: str, **params):
        _headers = {
            "Cache-Control": "no-cache",
            "x-api-key": api_key,
        }
        self._client = APIClient(headers=_headers)

        # Load configuration file
        self._config_ = load_yaml(path=CONFIG_PATH)
        assert self._config_, "Configuration not found"

        # Load endpoint settings
        name = self.__class__.__name__
        info = self._config_["endpoints"].get(name, {})
        if not info:
            raise ValueError(f"Endpoint '{name}' not found")
        self.info = {**{"name": name}, **info}
        self.params = self._get_params(params)
        self.url = self._get_url()

    def __help__(self) -> dict:
        """
        Return endpoint documentation string.
        Returns:
            dict: Documentation string.
        """
        return self.info

    def _get_url(self) -> str:
        """
        Construct the full URL by replacing
        path placeholders with actual parameters.
        Returns:
            str: The full URL for the endpoint.
        """
        server = self._config_["server"].strip("/")
        path = self.info["path"].strip("/")
        for key, value in self.params.items():
            path = path.replace(f"{{{key}}}", str(value))
        return f"{server}/{path}"

    def _validate_required_params(self, params: dict) -> None:
        """
        Validate that all required parameters are present.
        Args:
            params (dict): Parameters to validate.
        Raises:
            ValueError: If any required parameter is missing.
        """
        required_params = self.info.get("required_params", [])
        if required_params:
            missing = [p for p in required_params if p not in params]
            if missing:
                raise ValueError(f"Missing required parameters: {missing}")

    def _get_params(self, params: dict) -> dict:
        """
        Merge user-supplied params with optional defaults
        and validate required parameters.
        Args:
            params (dict): User-supplied parameters.
        Returns:
            dict: Merged parameters.
        """
        params = params or {}
        self._validate_required_params(params)
        optional = self.info.get("optional_params", {}) or {}
        return {**optional, **params}

    def _respect_rate_limits(self) -> None:
        """Throttle so we never exceed 10 calls per minute."""
        per_minute = self._config_["limitation"].get("max_call_per_minute", 10)
        interval = 60.0 / per_minute

        now = time.time()
        if self._request_timestamps:
            elapsed = now - self._request_timestamps[-1]
            if elapsed < interval:
                sleep_for = interval - elapsed
                time.sleep(sleep_for)

        # record this call
        self._request_timestamps.append(time.time())

    def _log_pagination_info(self, response: dict) -> None:
        """
        Log pagination information from the response.
        Args:
            response (dict): API response containing pagination info.
        """
        global total_rows, last_page

        pagination = response.get("pagination", {})

        if pagination:
            per_page = pagination.get("perPage")
            current_page = pagination.get("currentPage")
            from_row = pagination.get("from")
            to_row = pagination.get("to")
        else:
            raise ValueError("Pagination dict missing from response")

        # due to non-unique pagination response
        if current_page == 1:
            total_rows = pagination.get("total")
            last_page = pagination.get("lastPage")
            logger.info(
                f"Paginating {last_page} pages "
                f"for {total_rows} rows "
                f"with {per_page} rows per page"
            )

        logger.info(
            f"Fetched page {current_page}/{last_page}, rows {from_row} to {to_row}"
        )

    def get(self, verbose: bool = True) -> list[dict] | dict:
        """
        Perform GET request with pagination + throttling.
        Args:
            verbose (bool, optional): Whether to log pagination results.
        Returns:
            list[dict] | dict: Response of the Get request.
        """
        page_size = self.info.get("optional_params", {}).get("pageSize", None)

        # for endpoints with no pagination → single call
        if not page_size:
            self._respect_rate_limits()
            return self._client.get(self.url, self.params)

        # for endpoints with pagination → multiple calls
        all_data = []
        last_page = None  # init var
        page = 1
        while True:
            self._respect_rate_limits()
            params = {
                **self.params,
                "page": page,
                "pageSize": page_size,
            }
            response = self._client.get(self.url, params)

            # collect data + log if needed
            all_data.extend(response.get("data", []))
            if verbose:
                self._log_pagination_info(response)

            # check page
            pagination = response.get("pagination", {})
            current_page = pagination["currentPage"]
            if page == 1:
                last_page = pagination["lastPage"]
            if current_page == last_page:
                break

            # go to next page, if any
            page += 1

        return all_data


# ---------------------------------------------------------


class GetActiveNotifications(Endpoint):
    """
    Return list of active service notification or empty response.
    """

    pass


class GetDataset(Endpoint):
    """
    Returns metadata of a single dataset
    or 404 error if not found
    """

    pass


class GetDatasetData(Endpoint):
    """
    Returns data of a single dataset
    or empty array if no data is found
    """

    pass


class GetDatasetFile(Endpoint):
    """
    Return a single datasetfile
    or 404 error if not found
    """

    pass


class GetDatasetFileData(Endpoint):
    """
    Returns datasetfiledata or 404 error if not found
    or a 422 error if validation fails.
    """

    pass


class GetDatasetShorts(Endpoint):
    """
    Returns metadata of all public datasets, with pagination.
    If no parameters are given, returns all datasets sorted by dataset ID.
    If search parameter is given, returns datasets sorted by relevance.
    """

    pass


class GetHealthStatus(Endpoint):
    """
    Returns status of services
    """

    pass


class GetLastDataByDataset(Endpoint):
    """
    Return a last data by dataset
    or 404 error if not found
    """

    pass


class GetMultipleTimeseriesData(Endpoint):
    """
    Returns time series data of multiple datasets.
    """

    pass
