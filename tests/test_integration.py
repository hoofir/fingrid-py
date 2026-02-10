import os

import pandas as pd
import pytest
from dotenv import load_dotenv

from fingrid.endpoint import (
    GetActiveNotifications,
    GetDataset,
    GetDatasetData,
    GetDatasetShorts,
    GetHealthStatus,
    GetLastDataByDataset,
    GetMultipleTimeseriesData,
    GetUpdatedTimeseriesData,
)
from fingrid.utils import get_data, get_series_metadata

load_dotenv()

# -------------------------------------------

# Skip integration tests when API key not provided
API_KEY = os.getenv("FINGRID_API_KEY")
if not API_KEY:
    pytest.skip(
        "FINGRID_API_KEY not set — integration tests skipped", 
        allow_module_level=True
    )

# -------------------------------------------


def test_get_health_status():
    """Test GetHealthStatus.get() returns response."""
    ep = GetHealthStatus(API_KEY)
    resp = ep.get(verbose=False)
    assert resp is not None


def test_get_active_notifications():
    """Test GetActiveNotifications.get() returns response."""
    ep = GetActiveNotifications(API_KEY)
    resp = ep.get(verbose=False)
    assert resp is not None


def test_get_dataset_shorts():
    """Test GetDatasetShorts.get() returns list."""
    resp = GetDatasetShorts(API_KEY).get(verbose=False)
    if isinstance(resp, dict):
        resp = [resp]
    assert isinstance(resp, list)
    assert len(resp) > 0


def test_get_dataset():
    """Test GetDataset.get() with valid dataset ID."""
    resp = GetDataset(API_KEY, datasetId=317).get(verbose=False)
    assert resp is not None


def test_get_dataset_data():
    """Test GetDatasetData.get() with time range."""    
    resp = GetDatasetData(
        API_KEY,
        datasetId=317,
        startTime="2026-01-01T00:00:00Z",
        endTime="2026-01-02T00:00:00Z",
    ).get(verbose=False)
    assert resp is not None


def test_get_last_data_by_dataset():
    """Test GetLastDataByDataset.get() returns response."""    
    resp = GetLastDataByDataset(
        API_KEY, 
        datasetId=245
    ).get(verbose=False)
    assert resp is None or isinstance(resp, (dict, list))


def test_get_multiple_timeseries_data():
    """Test GetMultipleTimeseriesData.get() with single dataset."""    
    resp = GetMultipleTimeseriesData(
        API_KEY,
        datasets=[317,334,277],
        startTime="2026-01-01T00:00:00Z",
        endTime="2026-01-02T00:00:00Z",
    ).get(verbose=False)
    assert resp is not None


def test_get_updated_timeseries_data():
    """Test GetUpdatedTimeseriesData.get() with recent days."""    
    resp = GetUpdatedTimeseriesData(
        API_KEY,
        datasets=317,
        days=1,
    ).get(verbose=False)
    assert resp is not None


# -------------------------------------------


def test_get_series_metadata():
    """Test get_series_metadata returns DataFrame with valid data."""
    df = get_series_metadata(API_KEY, to_dataframe=True)
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "id" in df.columns


def test_get_data():
    """Test get_data returns DataFrame with valid data."""
    df = get_data(
        API_KEY,
        ids=317,
        start="2026-01-01T00:00:00Z",
        end="2026-01-02T00:00:00Z",
        verbose=False,
        to_dataframe=True,
    )
    assert isinstance(df, pd.DataFrame)

