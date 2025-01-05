import pytest
from app import create_app

@pytest.fixture
def client():
    # Create the app with the testing configuration
    app = create_app(config_name='testing')

    # Provide a test client
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_index_route_renders_correct_template(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'dashboard.html' in response.data

def test_set_input_valid_type(client):
    response = client.post('/set-input', json={'input_type': 'PC'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['input_type'] == 'PC'

def test_set_input_invalid_type(client):
    response = client.post('/set-input', json={'input_type': 'InvalidType'})
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'Invalid input type'

def test_get_input_type(client):
    client.post('/set-input', json={'input_type': 'Controller'})
    response = client.get('/get-input')
    assert response.status_code == 200
    assert response.json['input_type'] == 'Controller'

def test_get_chart_data(client):
    response = client.get('/api/chart-data')
    assert response.status_code == 200
    assert 'labels' in response.json
    assert 'datasets' in response.json

def test_reset_chart_data(client):
    response = client.post('/reset-chart')
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_serve_screenshot_file(client):
    response = client.get('/screenshots/test.png')
    assert response.status_code == 200

def test_get_screenshots_list(client):
    response = client.get('/api/screenshots')
    assert response.status_code == 200
    assert 'screenshots' in response.json

def test_set_game_outcome_valid(client):
    response = client.post('/set-game-outcome', json={'outcome': 'win'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert 'folder' in response.json

def test_set_game_outcome_invalid(client):
    response = client.post('/set-game-outcome', json={})
    assert response.status_code == 400
    assert response.json['status'] == 'error'
    assert response.json['message'] == 'No game outcome provided'