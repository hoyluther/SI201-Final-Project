# gather_audiodb.py
import sqlite3
import re
from db_setup import DB_NAME
from theaudiodb_api import get_track_details


# ----------------------------------------------------------
# Title Normalization Helpers
# ----------------------------------------------------------

def remove_featuring(text):
    """Remove 'featuring', 'ft.', 'feat.' and everything after."""
    return re.sub(r"\b(feat|ft|featuring|feat\.|ft\.)\b.*", "", text, flags=re.IGNORECASE).strip()


def clean_title_for_audiodb(title):
    """Clean title to improve AudioDB lookup."""
    t = title

    # 1. Remove featuring parts
    t = remove_featuring(t)

    # 2. Replace & with 'and'
    t = t.replace("&", "and")

    # 3. Remove punctuation
    t = (
        t.replace("’", "'")
         .replace("`", "'")
         .replace("!", "")
         .replace("?", "")
         .replace(",", "")
         .replace(".", "")
         .replace("(", "")
         .replace(")", "")
         .strip()
    )

    # 4. Clean multiple spaces
    t = re.sub(r"\s+", " ", t).strip()

    return t


# ----------------------------------------------------------
# Database Helpers
# ----------------------------------------------------------

def get_tracks_missing_audiodb():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title
        FROM tracks
        WHERE genre IS NULL
           OR bpm IS NULL
           OR album_name IS NULL;
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def save_audiodb(track_id, info):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        UPDATE tracks
        SET genre = ?, mood = ?, bpm = ?, album_name = ?, album_thumb = ?
        WHERE id = ?
    """, (
        info.get("strGenre"),
        info.get("strMood"),
        info.get("intTempo"),
        info.get("strAlbum"),
        info.get("strTrackThumb"),
        track_id,
    ))

    conn.commit()
    conn.close()


# ----------------------------------------------------------
# Main Pipeline
# ----------------------------------------------------------

def gather_audiodb():
    tracks = get_tracks_missing_audiodb()
    print(f"Tracks missing AudioDB: {len(tracks)}")

    if not tracks:
        print("All tracks already have AudioDB metadata.")
        return

    for track_id, title in tracks:
        print(f"\n🎧 Fetching AudioDB for: {title}")

        # Generate possible matches
        attempts = []

        # 1. Exact title
        attempts.append(title)

        # 2. Cleaned title (remove featuring + punctuation)
        cleaned = clean_title_for_audiodb(title)
        if cleaned not in attempts:
            attempts.append(cleaned)

        # 3. Remove apostrophes
        no_apostrophes = cleaned.replace("'", "")
        if no_apostrophes not in attempts:
            attempts.append(no_apostrophes)

        # 4. Remove trailing apostrophe slang (Darlin' → Darlin)
        if cleaned.endswith("'"):
            attempts.append(cleaned[:-1])

        # Remove duplicates while keeping order
        seen = set()
        attempts = [x for x in attempts if not (x in seen or seen.add(x))]

        info = None
        for attempt in attempts:
            print(f"   🔎 Trying title: {attempt}")
            info = get_track_details(attempt)
            if info:
                print("   ✅ AudioDB match found!")
                break

        if not info:
            print("   ❌ No AudioDB match after all attempts — skipping.")
            continue

        save_audiodb(track_id, info)
        print("   💾 Saved AudioDB metadata.")

    print("\n🎉 AudioDB stage complete.")


if __name__ == "__main__":
    gather_audiodb()
