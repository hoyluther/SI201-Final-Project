# gather_lyrics.py
# Robust lyrics collector for SI 201 Final Project
# Maximizes lyric retrieval with retries, normalization, and failure caching.

import sqlite3
import requests
import time

from db_setup import DB_NAME

LYRICS_URL = "https://api.lyrics.ovh/v1/{artist}/{title}"

# -------------------------------
# Helpers
# -------------------------------

def normalize(text):
    """Normalize strings to improve Lyrics.ovh hit rate."""
    return (
        text.replace("&", "and")
            .replace("’", "'")
            .replace("`", "'")
            .replace("(", "")
            .replace(")", "")
            .replace("!", "")
            .replace("?", "")
            .replace(",", "")
            .replace(".", "")
            .strip()
    )


def fetch_lyrics(artist, title):
    """Fetch lyrics with retry logic and timeout protection."""
    url = LYRICS_URL.format(artist=artist, title=title)

    for attempt in range(2):  # Try maximum twice
        try:
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                if "lyrics" in data and data["lyrics"].strip():
                    return data["lyrics"]
            else:
                return None  # No point retrying for 404, 500, etc.
        except requests.exceptions.Timeout:
            print(" Timeout — retrying…")
            time.sleep(1)
        except requests.exceptions.RequestException:
            return None

    return None  # Failed twice


def get_tracks_missing_lyrics():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT tracks.id, artists.name, tracks.title
        FROM tracks
        JOIN artists ON artists.id = tracks.artist_id
        LEFT JOIN lyrics ON lyrics.track_id = tracks.id
        WHERE lyrics.track_id IS NULL;
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def mark_failure(track_id):
    """Insert a placeholder so we never retry permanently failing songs."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO lyrics (track_id, lyrics_text) VALUES (?, ?)", 
                (track_id, None))
    conn.commit()
    conn.close()


def save_lyrics(track_id, lyrics_text):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO lyrics (track_id, lyrics_text) VALUES (?, ?)",
        (track_id, lyrics_text)
    )
    conn.commit()
    conn.close()


# -------------------------------
# Main Logic
# -------------------------------

def gather_lyrics():
    tracks = get_tracks_missing_lyrics()
    print(f"Tracks missing lyrics: {len(tracks)}")

    if not tracks:
        return

    for track_id, artist, title in tracks:

        print(f"\nFetching: {artist} – {title}")

        # Try original first
        lyrics = fetch_lyrics(artist, title)

        # Try normalized version if needed
        if not lyrics:
            art_norm = normalize(artist)
            title_norm = normalize(title)
            if (art_norm, title_norm) != (artist, title):
                print(f" Trying normalized: '{art_norm}' / '{title_norm}'")
                lyrics = fetch_lyrics(art_norm, title_norm)

        # Save or mark failure
        if lyrics:
            save_lyrics(track_id, lyrics)
            print("  Saved lyrics.")
        else:
            mark_failure(track_id)
            print("  Failed twice — marked as no-lyrics.")

        # Short sleep to avoid rate limiting
        time.sleep(0.4)


if __name__ == "__main__":
    gather_lyrics()