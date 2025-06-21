import sqlite3

DB_PATH = "whitelist.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mc_username TEXT NOT NULL,
            discord_username TEXT NOT NULL,
            uuid TEXT NOT NULL,
            op INTEGER DEFAULT 0
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS blocked_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_username TEXT,
            mc_username TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_player(mc_username, discord_username, uuid, op=0):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO players (mc_username, discord_username, uuid, op)
        VALUES (?, ?, ?, ?)
    ''', (mc_username, discord_username, uuid, op))
    conn.commit()
    conn.close()

def get_player_by_discord(discord_username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM players WHERE discord_username = ?', (discord_username,))
    result = c.fetchone()
    conn.close()
    return result

def list_players():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT mc_username, discord_username, uuid, op FROM players')
    results = c.fetchall()
    conn.close()
    return results

def block_user(discord_username=None, mc_username=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO blocked_users (discord_username, mc_username)
        VALUES (?, ?)
    ''', (discord_username, mc_username))
    conn.commit()
    conn.close()

def is_blocked(discord_username=None, mc_username=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if discord_username and mc_username:
        c.execute('SELECT 1 FROM blocked_users WHERE discord_username = ? OR mc_username = ?', (discord_username, mc_username))
    elif discord_username:
        c.execute('SELECT 1 FROM blocked_users WHERE discord_username = ?', (discord_username,))
    elif mc_username:
        c.execute('SELECT 1 FROM blocked_users WHERE mc_username = ?', (mc_username,))
    else:
        conn.close()
        return False
    result = c.fetchone()
    conn.close()
    return bool(result)

def remove_player_by_discord(discord_username):
    import sqlite3
    conn = sqlite3.connect("whitelist.db")
    c = conn.cursor()
    c.execute('DELETE FROM players WHERE discord_username = ?', (discord_username,))
    conn.commit()
    conn.close()
