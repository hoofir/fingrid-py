from fingrid.client import APIClient


def test_client_headers():
    headers = {"x-api-key": "fake-key"}
    client = APIClient(headers=headers)
    assert client.session.headers["x-api-key"] == "fake-key"
    client.close()


def test_client_close():
    client = APIClient(headers={})
    client.close()
    assert True


def test_get_success(requests_mock):
    url = "http://example.com/data"
    data = {"value": 42}
    requests_mock.get(url, json=data, status_code=200)

    client = APIClient({"x-api-key": "fake"})
    response = client.get(url)
    assert response == data
    client.close()


def test_get_http_error(requests_mock, caplog):
    url = "http://example.com/error"
    # Simulate HTTPError
    requests_mock.get(url, status_code=404, text="Not Found")

    client = APIClient({"x-api-key": "fake"})
    with caplog.at_level("INFO"):
        result = client.get(url)

    # APIClient.get() returns None on HTTPError
    assert result is None
    # It logs "HTTP error"
    assert "HTTP error" in caplog.text
    client.close()
