import sqlite3

DB_NAME = "music_project.db"


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Artists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    # Tracks
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER,
            title TEXT,
            UNIQUE(artist_id, title),
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        )
    """)

    # Lyrics
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lyrics (
            track_id INTEGER PRIMARY KEY,
            lyrics_text TEXT,
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        )
    """)

    # Charts (normalized chart names + dates)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            chart_date TEXT,
            UNIQUE(name, chart_date)
        )
    """)

    # Chart entries (normalized)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chart_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chart_id INTEGER,
            track_id INTEGER,
            chart_position INTEGER,
            UNIQUE(chart_id, track_id),
            FOREIGN KEY (chart_id) REFERENCES charts(id),
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        )
    """)

    # REQUIRED by gather_charts.py
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chart_popularity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER NOT NULL,
            chart_name TEXT NOT NULL,
            chart_position INTEGER NOT NULL,
            chart_date TEXT NOT NULL,
            UNIQUE(track_id, chart_name, chart_date),
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Tables created successfully.")


if __name__ == "__main__":
    create_tables()
