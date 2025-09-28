from unittest.mock import patch

import pandas as pd
import pytest

from fingrid.utils import get_data, get_series_metadata


# -----------------------------
#   Tests get_series_metadata
# -----------------------------
def test_get_series_metadata_dict():
    fake_md = [{"id": 1, "name": "Series1"}, {"id": 2, "name": "Series2"}]
    with patch("fingrid.endpoint.GetDatasetShorts.get", return_value=fake_md):
        result = get_series_metadata("fake_key", to_dataframe=False)
        assert isinstance(result, list)  # returns list/dict
        assert result == fake_md


def test_get_series_metadata_df():
    fake_md = [{"id": 2, "name": "B"}, {"id": 1, "name": "A"}]
    with patch("fingrid.endpoint.GetDatasetShorts.get", return_value=fake_md):
        result = get_series_metadata("fake_key", to_dataframe=True)
        assert isinstance(result, pd.DataFrame)
        # check sorting by id
        assert list(result["id"]) == [1, 2]


def test_get_series_metadata_handles_exception():
    with patch(
        "fingrid.endpoint.GetDatasetShorts.get", side_effect=Exception("API fail")
    ):
        with pytest.raises(Exception, match="API fail"):
            get_series_metadata("fake_key", to_dataframe=True)


# -----------------------------
#   Tests get_data
# -----------------------------
def test_get_data_with_single_id_string():
    fake_data = [{"datasetId": "1", "startTime": "2025-09-21T00:00:00Z", "value": 10}]
    with patch(
        "fingrid.endpoint.GetMultipleTimeseriesData.get", return_value=fake_data
    ):
        result = get_data(
            "fake_key", ids="1", start="2025-01-01T00:00:00Z", to_dataframe=False
        )
        assert isinstance(result, list)
        assert result == fake_data


def test_get_data_with_single_id_int():
    fake_data = [{"datasetId": 1, "startTime": "2025-09-21T00:00:00Z", "value": 10}]
    with patch(
        "fingrid.endpoint.GetMultipleTimeseriesData.get", return_value=fake_data
    ):
        result = get_data(
            "fake_key", ids="1", start="2025-01-01T00:00:00Z", to_dataframe=False
        )
        assert isinstance(result, list)
        assert result == fake_data


def test_get_data_with_list_of_ids_df():
    fake_data = [
        {"datasetId": "1", "startTime": "2025-09-21T00:00:00Z", "value": 10},
        {"datasetId": "2", "startTime": "2025-09-21T00:00:00Z", "value": 20},
    ]
    with patch(
        "fingrid.endpoint.GetMultipleTimeseriesData.get", return_value=fake_data
    ):
        result = get_data(
            "fake_key", ids=[1, 2], start="2025-01-01T00:00:00Z", to_dataframe=True
        )
        assert isinstance(result, pd.DataFrame)
        # Check that DataFrame is sorted by datasetId
        assert list(result["datasetId"]) == ["1", "2"]


def test_get_data_with_invalid_ids_type():
    with pytest.raises(TypeError):
        get_data("fake_key", ids=3.1415, start="2025-01-01T00:00:00Z")


def test_get_data_handles_exception():
    with patch(
        "fingrid.endpoint.GetMultipleTimeseriesData.get",
        side_effect=Exception("API fail"),
    ):
        with pytest.raises(Exception, match="API fail"):
            get_data("fake_key", ids="1", start="2025-01-01T00:00:00Z")
