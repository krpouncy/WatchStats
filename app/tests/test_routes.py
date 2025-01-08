import os
import shutil
import tempfile

import pytest
from flask import Flask, json

from app.core.routes import core_bp
from app.core.state import app_state


@pytest.fixture
def client():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Override the app_state base path to use the temporary directory
    app_state.base_path = temp_dir
    app_state.screenshot_folder = os.path.join(temp_dir, 'screenshots')
    app_state.model_directory = os.path.join(temp_dir, 'models')
    app_state.user_components_directory = os.path.join(temp_dir, 'user_components')

    # Create necessary directories
    os.makedirs(app_state.screenshot_folder, exist_ok=True)
    os.makedirs(app_state.model_directory, exist_ok=True)
    os.makedirs(app_state.user_components_directory, exist_ok=True)

    app = Flask(__name__)
    app.register_blueprint(core_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

    # Clean up the temporary directory after tests
    shutil.rmtree(temp_dir)


class TestRoutes:

    def test_dashboard_route(self, client):
        response = client.get('/')
        assert response.status_code == 200
        assert b'Dashboard' in response.data

    def test_set_input_valid(self, client):
        response = client.post('/set-input', json={'input_type': 'PC'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['input_type'] == 'PC'

    def test_set_input_invalid(self, client):
        response = client.post('/set-input', json={'input_type': 'InvalidType'})
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert data['message'] == 'Invalid input type'

    def test_about_route(self, client):
        response = client.get('/about')
        assert response.status_code == 200
        assert b'About' in response.data

    def test_load_route(self, client):
        response = client.get('/load')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_get_input(self, client):
        app_state.input_type = 'Controller'
        response = client.get('/get-input')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['input_type'] == 'Controller'

    def test_reset_input(self, client):
        response = client.post('/reset-input')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert app_state.input_type is None

    def test_serve_screenshot(self, client):
        # Assuming a file named 'test.png' exists in the screenshot folder
        response = client.get('/screenshots/test.png')
        assert response.status_code == 200

    def test_get_screenshots(self, client):
        response = client.get('/api/screenshots')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'screenshots' in data

    def test_save_layout(self, client):
        layout_data = {
            'layout': [
                {'parent': 'user1', 'id': 'user1_component1', 'x': 0, 'y': 0, 'width': 100, 'height': 100}
            ]
        }
        response = client.post('/save_layout', json=layout_data)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'

    def test_set_game_outcome(self, client):
        response = client.post('/set-game-outcome', json={'outcome': 'win'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'folder' in data
        # remove the folder after the test
        shutil.rmtree(data['folder'])
