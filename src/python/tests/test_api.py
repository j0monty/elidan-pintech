from http import HTTPStatus
from unittest.mock import patch

from fastapi.testclient import TestClient
from pymongo.errors import ConnectionFailure
from services.pintech_api.main import app

test_client = TestClient(app)


def test_healthcheck_success():
    with patch('services.pintech_api.main.MongoClient') as mock_client:
        # Mock successful MongoDB connection
        mock_client.return_value.admin.command.return_value = True

        response = test_client.get('/healthcheck')
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'API': 'OK', 'Datastore': 'OK'}


def test_healthcheck_failure():
    with patch('services.pintech_api.main.MongoClient') as mock_client:
        # Mock failed MongoDB connection
        mock_client.return_value.admin.command.side_effect = ConnectionFailure('Connection failed')

        response = test_client.get('/healthcheck')
        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
        assert response.json() == {'API': 'OK', 'Datastore': 'FAILED'}


def test_version():
    response = test_client.get('/version')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'Version': '0.1'}
