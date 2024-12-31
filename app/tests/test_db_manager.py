import pytest
import sqlite3
from app.core.db_manager import initialize_database, save_game_data, save_snapshot_data, save_team_data

@pytest.fixture(autouse=True)
def test_setup_and_teardown():
    initialize_database()
    yield
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS team_data')
    cursor.execute('DROP TABLE IF EXISTS snapshot_data')
    cursor.execute('DROP TABLE IF EXISTS game_data')
    conn.commit()
    conn.close()

def test_saves_game_data_correctly():
    game_id = save_game_data('Game details', 'win')
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM game_data WHERE id = ?', (game_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == 'Game details'
    assert row[2] == 'win'
    conn.close()

def test_saves_snapshot_data_correctly():
    game_id = save_game_data('Game details', 'win')
    snapshot_id = save_snapshot_data(game_id, 'Header text')
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM snapshot_data WHERE id = ?', (snapshot_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == game_id
    assert row[2] == 'Header text'
    conn.close()

def test_saves_team_data_correctly():
    game_id = save_game_data('Game details', 'win')
    snapshot_id = save_snapshot_data(game_id, 'Header text')
    save_team_data(snapshot_id, 'Player 1', 'Stats', 1)
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM team_data WHERE snapshot_id = ?', (snapshot_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == snapshot_id
    assert row[2] == 'Player 1'
    assert row[3] == 'Stats'
    assert row[4] == 1
    conn.close()

def test_handles_null_win_or_lose():
    game_id = save_game_data('Game details')
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM game_data WHERE id = ?', (game_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == 'Game details'
    assert row[2] is None
    conn.close()

def test_handles_empty_details():
    game_id = save_game_data('')
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM game_data WHERE id = ?', (game_id,))
    row = cursor.fetchone()
    assert row is not None
    assert row[1] == ''
    conn.close()