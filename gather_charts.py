# gather_charts.py
import sqlite3
import datetime
import requests
from bs4 import BeautifulSoup

from db_setup import DB_NAME

CHART_URL = "https://www.billboard.com/charts/hot-100"
CHART_NAME = "Billboard Hot 100"
BATCH_LIMIT = 25 


def fetch_chart_html(url=CHART_URL):
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.text
    except requests.exceptions.RequestException as e:
        print("Error fetching chart page:", e)
        return None


def parse_chart(html):
    soup = BeautifulSoup(html, "html.parser")
    entries = []

    rows = soup.select("li.o-chart-results-list__item")
    rank = 1
    for row in rows:
        title_tag = row.find("h3")
        artist_tag = row.find("span", class_="c-label")

        if not title_tag or not artist_tag:
            continue

        title = title_tag.get_text(strip=True)
        artist = artist_tag.get_text(strip=True)

        if not title or not artist:
            continue

        entries.append({"rank": rank, "title": title, "artist": artist})
        rank += 1

    print(f"Parsed {len(entries)} chart entries from page.")
    return entries


def find_track_id(conn, artist_name, title):
    cur = conn.cursor()
    cur.execute("SELECT id FROM artists WHERE name = ?", (artist_name,))
    row = cur.fetchone()
    if not row:
        return None
    artist_id = row[0]

    cur.execute(
        "SELECT id FROM tracks WHERE artist_id = ? AND title = ?",
        (artist_id, title),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    return None


def insert_chart_row(conn, track_id, chart_name, chart_position, chart_date):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO chart_popularity
            (track_id, chart_name, chart_position, chart_date)
        VALUES (?, ?, ?, ?)
        """,
        (track_id, chart_name, chart_position, chart_date)
    )
    return cur.rowcount  # 1 if inserted, 0 if duplicate ignored


def gather_chart_data():
    html = fetch_chart_html()
    if not html:
        return

    entries = parse_chart(html)
    if not entries:
        print("No chart entries parsed.")
        return

    conn = sqlite3.connect(DB_NAME)
    inserted = 0
    today = datetime.date.today().isoformat()

    for entry in entries:
        if inserted >= BATCH_LIMIT:
            break

        artist = entry["artist"]
        title = entry["title"]
        rank = entry["rank"]

        track_id = find_track_id(conn, artist, title)

        if track_id is None:
            print(f"Skipping unmatched chart entry: {artist} - {title}")
            continue

        print(f"Match found: {artist} - {title} (track_id={track_id})")

        rows_added = insert_chart_row(
            conn, track_id, CHART_NAME, rank, today
        )

        if rows_added > 0:
            inserted += 1
            print(
                f"Saved chart row #{inserted}: rank {rank} – {artist} - {title}"
            )

    conn.commit()
    conn.close()
    print("Done; inserted", inserted, "new matching rows.")


if __name__ == "__main__":
    gather_chart_data()