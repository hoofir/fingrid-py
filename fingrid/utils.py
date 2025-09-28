import logging
import os
from collections.abc import Iterable

import pandas as pd
import yaml

logging.basicConfig(
    force=True,
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_yaml(path: str) -> dict:
    """
    Load a YAML file.
    Args:
        path (str): Path to the YAML file.
    Returns:
        dict: Parsed YAML data.
    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be accessed.
        yaml.YAMLError: If the YAML content is invalid.
        ValueError: If the file is empty or content is not a dict.
    """
    try:
        if not os.path.exists(path):
            raise FileNotFoundError(f"YAML file not found: {path}")
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        if not isinstance(config, dict):
            raise ValueError(f"YAML file is not a valid dictionary: {path}")
        return config
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except PermissionError:
        logger.error(f"Error: Permission denied while accessing '{path}'")
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file '{path}': {e}")
    except Exception as e:
        logger.error(f"Unexpected error while loading YAML: {e}")
    return {}


def get_series_metadata(
    api_key: str, to_dataframe: bool = False
) -> list[dict] | pd.DataFrame:
    """
    Utility function to get all series' metadata from GetDatasetShorts endpoint.
    Args:
        api_key (str): Personal API key for authentication.
        to_dataframe (bool, optional): Whether to convert to Pandas.DataFrame. Defaults to True.
    Returns:
        list[dict[str, Any]] | pd.DataFrame: DataFrame containing series metadata.
    """
    from .endpoint import GetDatasetShorts  # noqa: F811

    try:
        md = GetDatasetShorts(api_key).get(verbose=False)
        if isinstance(md, dict):
            md = [md]  # wrap single dict into a list
        if to_dataframe:
            md_df = pd.DataFrame(md).sort_values("id")
            return md_df.reset_index(drop=True)
        return md
    except Exception as e:
        logger.error(f"Error retrieving metadata: {e}")
        raise


def get_data(
    api_key: str,
    ids: int | str | Iterable[str | int],
    start: str | pd.Timestamp,
    end: str | pd.Timestamp | None = None,
    verbose: bool = True,
    to_dataframe: bool = True,
) -> list[dict] | pd.DataFrame:
    """
    Utility function to get data from GetMultipleTimeseriesData endpoint.
    Args:
        api_key (str): Personal API key for authentication.
        id_list (str | int | Iterable[str | int]): Timeseries ID(s) to retrieve data for.
        start (str | pd.Timestamp): Start time (UTC) in ISO 8601 format.
        end (str | pd.Timestamp | None, optional): End time (UTC) in ISO 8601 format. Defaults to None.
        verbose (bool, optional): Whether to log the pagination results. Defaults to True.
        to_dataframe (bool, optional): Whether to convert to Pandas.DataFrame. Defaults to True.
    Returns:
        pd.DataFrame: DataFrame containing given series' data.
    """
    from .endpoint import GetMultipleTimeseriesData  # noqa: F811

    # convert given ID(s) to suitable format for endpoint
    if isinstance(ids, (int, str)):
        ids = str(ids)
    elif isinstance(ids, Iterable):
        ids = ", ".join(str(x) for x in ids)
    else:
        raise TypeError("Unknown type for parameter: ids")

    # handle end time
    if not end:
        next10days = pd.Timestamp.now(tz="UTC") + pd.Timedelta(days=10)
        assert isinstance(next10days, pd.Timestamp)  # convinces Pyright
        end = next10days.isoformat(timespec="seconds")

    params = {"datasets": ids, "startTime": str(start), "endTime": str(end)}

    try:
        data = GetMultipleTimeseriesData(api_key, **params).get(verbose)
        if isinstance(data, dict):
            data = [data]  # wrap single dict into a list
        if to_dataframe:
            data_df = pd.DataFrame(data).sort_values(["datasetId", "startTime"])
            return data_df.reset_index(drop=True)
        else:
            return data
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise
