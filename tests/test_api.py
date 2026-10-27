
import pytest
import requests

import first_request


def test_api_failure_stops_pipeline(monkeypatch):
    def mock_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError(
            "Simulated connection failure"
        )

    monkeypatch.setattr(first_request.requests, "get", mock_get)

    with pytest.raises(SystemExit, match="Request failed"):
        first_request.main()
