import tempfile

import pytest
import yaml

from fingrid.endpoint import Endpoint, load_yaml


# --------------------------
#   Test 'load_yaml'
# --------------------------
def test_load_yaml():
    mock_config = {"hello": "world"}
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        yaml.dump(mock_config, f)
        f.flush()
        loaded_config = load_yaml(f.name)
        assert loaded_config == mock_config


# --------------------------
#   Fake config for testing
# --------------------------
fake_config = {
    "server": "http://api.test",
    "endpoints": {
        "FakeEndpoint": {
            "path": "datasets/{id}",
            "required_params": ["id"],
            "optional_params": {"pageSize": 2},  # needed for pagination test
        }
    },
    "limitation": {"max_call_per_minute": 10},
}


# --------------------------
#   Test URL
# --------------------------
def test_url_construction(monkeypatch):
    monkeypatch.setattr("fingrid.endpoint.load_yaml", lambda path: fake_config)

    class FakeEndpoint(Endpoint):
        pass

    ep = FakeEndpoint(api_key="fake", id=123)
    assert ep.url == "http://api.test/datasets/123"


# --------------------------
#   Test params
# --------------------------
def test_missing_required_params(monkeypatch):
    monkeypatch.setattr("fingrid.endpoint.load_yaml", lambda path: fake_config)

    class FakeEndpoint(Endpoint):
        pass

    # Should raise ValueError because "id" is required
    with pytest.raises(ValueError) as e:
        FakeEndpoint(api_key="fake")
    assert "Missing required parameters" in str(e.value)


# --------------------------
#   Test pagination
# --------------------------
def test_pagination(monkeypatch, requests_mock):
    monkeypatch.setattr("fingrid.endpoint.load_yaml", lambda path: fake_config)

    class FakeEndpoint(Endpoint):
        pass

    ep = FakeEndpoint(api_key="fake", id=123)
    url = ep.url

    # Skip rate limiting in test
    monkeypatch.setattr(ep, "_respect_rate_limits", lambda: None)

    # Mock paginated responses
    requests_mock.get(
        url,
        [
            {
                "json": {
                    "data": [1, 2],
                    "pagination": {"currentPage": 1, "lastPage": 2},
                }
            },
            {
                "json": {
                    "data": [3, 4],
                    "pagination": {"currentPage": 2},
                }
            },
        ],
    )

    results = ep.get(verbose=False)
    assert results == [1, 2, 3, 4]
