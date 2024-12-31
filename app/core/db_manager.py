import sqlite3


def initialize_database():
    """
    Initialize the database with the necessary tables
    :return:
    """
    conn = sqlite3.connect('game_data.db')
    cursor = conn.cursor()

    # Create `game_data` table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            details TEXT NOT NULL,
            win_or_lose TEXT
        )
    ''')

    # Create `snapshot_data` table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS snapshot_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER,
            header_text TEXT,
            FOREIGN KEY (game_id) REFERENCES game_data(id)
        )
    ''')

    # Create `team_data` table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id INTEGER,
            player_name TEXT,
            stats TEXT,
            team_type INTEGER,
            FOREIGN KEY (snapshot_id) REFERENCES snapshot_data(id)
        )
    ''')

    conn.commit()
    conn.close()

def save_game_data(details, win_or_lose=None):
    """
    Save the game data to the database
    :param details:
    :param win_or_lose:
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect('game_data.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO game_data (details, win_or_lose) VALUES (?, ?)', (details, win_or_lose))
        conn.commit()
        game_id = cursor.lastrowid
        return game_id
    except sqlite3.Error as e:
        print(e)
        # tqdm.write(f"Database error in save_game_data: {e}")
    finally:
        conn.close()

def save_snapshot_data(game_id, header_text):
    """
    Save the snapshot data to the database
    :param game_id:
    :param header_text:
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect('game_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO snapshot_data (game_id, header_text)
            VALUES (?, ?)
        ''', (game_id, header_text))
        conn.commit()
        snapshot_id = cursor.lastrowid
        return snapshot_id
    except sqlite3.Error as e:
        print(e)
        # tqdm.write(f"Database error in save_snapshot_data: {e}")
    finally:
        conn.close()

def save_team_data(snapshot_id, player_name, stats, team_type):
    """
    Save the team data to the database
    :param snapshot_id:
    :param player_name:
    :param stats:
    :param team_type:
    :return:
    """
    conn = None
    try:
        conn = sqlite3.connect('game_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO team_data (snapshot_id, player_name, stats, team_type)
            VALUES (?, ?, ?, ?)
        ''', (snapshot_id, player_name, stats, team_type))
        conn.commit()
    except sqlite3.Error as e:
        print(e)
        # tqdm.write(f"Database error in save_team_data: {e}")
    finally:
        conn.close()