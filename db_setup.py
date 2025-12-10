# db_setup.py
# Clean SQLite schema for SI 201 final project (Genius + Lyrics + Billboard)

import sqlite3

DB_NAME = "music_project.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # --------------------------
    # ARTISTS
    # --------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS artists (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        );
    """)

    # --------------------------
    # TRACKS
    # --------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist_id INTEGER,
            title TEXT,
            genius_song_id INTEGER,
            UNIQUE(artist_id, title),
            FOREIGN KEY (artist_id) REFERENCES artists(id)
        );
    """)

    # --------------------------
    # LYRICS (from lyrics.ovh)
    # --------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS lyrics (
            track_id INTEGER PRIMARY KEY,
            lyrics_text TEXT,
            FOREIGN KEY (track_id) REFERENCES tracks(id)
        );
    """)

    # --------------------------
    # CHART POPULARITY (Billboard via BeautifulSoup)
    # --------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chart_popularity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            track_id INTEGER,
            chart_name TEXT,
            chart_position INTEGER,
            chart_date TEXT,
            -- Prevent duplicate chart rows on rerun
            UNIQUE(chart_name, chart_position, chart_date),
            FOREIGN KEY(track_id) REFERENCES tracks(id)
        );
    """)

    conn.commit()
    conn.close()
    print("Tables created in", DB_NAME)


if __name__ == "__main__":
    create_tables()