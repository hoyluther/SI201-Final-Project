# gather_genius.py
# Uses Genius API to gather artist + song title metadata
# Stores results in artists and tracks tables (no external IDs stored)

import os
import sqlite3
import requests

from db_setup import DB_NAME

GENIUS_TOKEN = os.environ.get("GENIUS_TOKEN")
BASE_URL = "https://api.genius.com/search"

BATCH_LIMIT = 25  # project requirement


def get_connection():
    return sqlite3.connect(DB_NAME)


def get_or_create_artist(cur, artist_name):
    cur.execute(
        "INSERT OR IGNORE INTO artists (name) VALUES (?)",
        (artist_name,)
    )
    cur.execute(
        "SELECT id FROM artists WHERE name = ?",
        (artist_name,)
    )
    row = cur.fetchone()
    return row[0] if row else None


def track_exists(cur, artist_id, title):
    cur.execute(
        """
        SELECT id FROM tracks
        WHERE artist_id = ? AND title = ?
        """,
        (artist_id, title)
    )
    return cur.fetchone() is not None


def search_genius(artist, title):
    if not GENIUS_TOKEN:
        return None

    headers = {"Authorization": f"Bearer {GENIUS_TOKEN}"}
    params = {"q": f"{artist} {title}"}

    resp = requests.get(BASE_URL, headers=headers, params=params, timeout=10)
    resp.raise_for_status()

    data = resp.json()
    hits = data.get("response", {}).get("hits", [])
    if not hits:
        return None

    return hits[0].get("result")


def add_song_to_db(conn, artist, title):
    cur = conn.cursor()

    artist_id = get_or_create_artist(cur, artist)
    if artist_id is None:
        print(f"Could not create/find artist: {artist}")
        return False

    if track_exists(cur, artist_id, title):
        print(f"Skipping existing: {artist} - {title}")
        return False

    genius_result = search_genius(artist, title)
    if not genius_result:
        print(f"No Genius result for {artist} - {title}")
        return False

    # IMPORTANT: tracks table does NOT have genius_song_id, so only insert columns that exist
    cur.execute(
        """
        INSERT OR IGNORE INTO tracks (artist_id, title)
        VALUES (?, ?)
        """,
        (artist_id, title)
    )

    conn.commit()
    print(f"Added track: {artist} - {title}")
    return True


def get_track_count(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tracks")
    return cur.fetchone()[0]


def gather_genius_data(song_list):
    if not GENIUS_TOKEN:
        print("GENIUS_TOKEN not set.")
        return

    conn = get_connection()
    added = 0

    for artist, title in song_list:
        if added >= BATCH_LIMIT:
            break

        if add_song_to_db(conn, artist, title):
            added += 1

    conn.close()
    print(f"New tracks added this run: {added}")


# Pipeline can import this
SONGS = [
    ("Mariah Carey", "All I Want for Christmas Is You"),
    ("Wham!", "Last Christmas"),
    ("Bobby Helms", "Jingle Bell Rock"),
]
def get_track_count(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tracks")
    return cur.fetchone()[0]

if __name__ == "__main__":
    gather_genius_data(SONGS)