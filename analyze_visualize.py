# analyze_visualize.py
# Cleaned analysis + visualization for SI 201 final project
# Requires: tracks, artists, lyrics, chart_popularity tables

import sqlite3
import os
import matplotlib.pyplot as plt

DB_NAME = "music_project.db"

# Ensure folder exists
os.makedirs("charts", exist_ok=True)


def fetch_query(query, params=()):
    """Helper to run a SQL query and return results."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows


# ----------------------------------------------------------------------
# 1. Average chart rank per artist
# ----------------------------------------------------------------------

def avg_chart_rank_per_artist():
    print("\n=== Average chart rank per artist ===")

    query = """
        SELECT artists.name, AVG(chart_popularity.chart_position)
        FROM chart_popularity
        JOIN tracks ON tracks.id = chart_popularity.track_id
        JOIN artists ON artists.id = tracks.artist_id
        GROUP BY artists.name
        ORDER BY AVG(chart_popularity.chart_position) ASC
        LIMIT 20;
    """

    data = fetch_query(query)

    if not data:
        print("No matching chart + track data (possible if many Billboard songs had no lyrics).")
        return None

    for name, avg_rank in data:
        print(f"{name:<25}  avg rank: {avg_rank:.2f}")

    # Plot bar chart
    artists = [row[0] for row in data]
    ranks = [row[1] for row in data]

    plt.figure(figsize=(10, 6))
    plt.barh(artists, ranks)
    plt.xlabel("Average Chart Rank (lower is better)")
    plt.title("Average Chart Rank per Artist")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("charts/avg_chart_rank.png")
    plt.close()


# ----------------------------------------------------------------------
# 2. Lyrics length vs. chart rank
# ----------------------------------------------------------------------

def lyrics_vs_chart_rank():
    print("\n=== Lyrics length vs chart rank ===")

    query = """
        SELECT chart_popularity.chart_position, lyrics.lyrics_text
        FROM chart_popularity
        JOIN lyrics ON lyrics.track_id = chart_popularity.track_id;
    """

    rows = fetch_query(query)

    if not rows:
        print("No joined lyrics + chart data available.")
        return

    x_positions = []
    y_wordcounts = []

    for pos, text in rows:
        if text:
            wc = len(text.split())
            x_positions.append(pos)
            y_wordcounts.append(wc)

    if not x_positions:
        print("No usable data points for scatter plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.scatter(x_positions, y_wordcounts)
    plt.xlabel("Chart Rank (1 = highest)")
    plt.ylabel("Lyrics Word Count")
    plt.title("Lyrics Length vs Chart Rank")
    plt.tight_layout()
    plt.savefig("charts/lyrics_vs_chart_rank.png")
    plt.close()

    print("Saved: charts/lyrics_vs_chart_rank.png")


# ----------------------------------------------------------------------
# 3. Lyrics length per artist
# ----------------------------------------------------------------------

def avg_lyrics_length_per_artist():
    print("\n=== Average lyrics length per artist ===")

    query = """
        SELECT artists.name, AVG(LENGTH(lyrics.lyrics_text)), COUNT(*)
        FROM lyrics
        JOIN tracks ON tracks.id = lyrics.track_id
        JOIN artists ON artists.id = tracks.artist_id
        GROUP BY artists.name
        ORDER BY AVG(LENGTH(lyrics.lyrics_text)) DESC
        LIMIT 20;
    """

    data = fetch_query(query)

    if not data:
        print("No lyrics stored.")
        return

    for name, avg_len, count in data:
        print(f"{name:<25} avg length: {avg_len:.1f} chars   from {count} song(s)")

    artists = [row[0] for row in data]
    avg_lengths = [row[1] for row in data]

    plt.figure(figsize=(10, 6))
    plt.barh(artists, avg_lengths)
    plt.xlabel("Average Lyrics Length (characters)")
    plt.title("Top Artists by Lyrics Length")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("charts/avg_lyrics_length.png")
    plt.close()

    print("Saved: charts/avg_lyrics_length.png")


# ----------------------------------------------------------------------
# 4. Chart rank histogram
# ----------------------------------------------------------------------

def chart_rank_histogram():
    print("\n=== Chart rank distribution ===")

    rows = fetch_query("SELECT chart_position FROM chart_popularity;")

    if not rows:
        print("No chart data found.")
        return

    positions = [row[0] for row in rows]

    plt.figure(figsize=(8, 5))
    plt.hist(positions, bins=25)
    plt.xlabel("Chart Position")
    plt.ylabel("Frequency")
    plt.title("Distribution of Chart Ranks")
    plt.tight_layout()
    plt.savefig("charts/chart_rank_histogram.png")
    plt.close()

    print("Saved: charts/chart_rank_histogram.png")


# ----------------------------------------------------------------------
# Main runner
# ----------------------------------------------------------------------

def main():
    avg_chart_rank_per_artist()
    lyrics_vs_chart_rank()
    avg_lyrics_length_per_artist()
    chart_rank_histogram()
    print("\nDone. Charts saved in /charts/ folder.")


if __name__ == "__main__":
    main()