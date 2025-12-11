# run_pipeline.py
from db_setup import create_tables, DB_NAME
from gather_genius import SONGS, track_exists, add_song_to_db, get_track_count
from gather_charts import gather_chart_data
from gather_lyrics import gather_lyrics
from gather_audiodb import gather_audiodb

def run_genius_stage():
    BATCH_LIMIT = 25
    TARGET_TOTAL = 100

    current = get_track_count()
    print("Current tracks in DB:", current)
    if current >= TARGET_TOTAL:
        print("Already reached target of", TARGET_TOTAL)
        return

    import sqlite3
    conn = sqlite3.connect(DB_NAME)
    new_added = 0

    for artist, title in SONGS:
        if new_added >= BATCH_LIMIT or current >= TARGET_TOTAL:
            break

        if track_exists(conn, artist, title):
            print("Skipping existing:", artist, "-", title)
            continue

        if add_song_to_db(conn, artist, title):
            new_added += 1
            current += 1

    conn.commit()
    conn.close()
    print("New tracks added this run:", new_added)
    print("Total tracks now (approx):", current)

def main():
    print("Creating tables…")
    create_tables()

    print("Filling tracks via Genius…")
    run_genius_stage()

    print("Gathering chart data…")
    gather_chart_data()

    print("Gathering lyrics…")
    gather_lyrics()

    print("Gathering AudioDB metadata…")
    gather_audiodb()

    print("Pipeline complete.")

if __name__ == "__main__":
    main()
