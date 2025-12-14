# calculations.py

import sqlite3
from db_setup import DB_NAME


# Pull data from the database and compute aggregates


def get_calculated_data():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Average chart rank per artist
    cur.execute("""
        SELECT 
            artists.name,
            AVG(chart_popularity.chart_position) AS avg_rank
        FROM chart_popularity
        JOIN tracks ON tracks.id = chart_popularity.track_id
        JOIN artists ON artists.id = tracks.artist_id
        GROUP BY artists.name
        HAVING avg_rank IS NOT NULL
        ORDER BY avg_rank ASC;
    """)
    avg_rank_rows = cur.fetchall()

    # Average lyrics length per artist (skip NULL lyrics)
    cur.execute("""
        SELECT 
            artists.name,
            AVG(LENGTH(lyrics.lyrics_text)) AS avg_lyric_length
        FROM lyrics
        JOIN tracks ON tracks.id = lyrics.track_id
        JOIN artists ON artists.id = tracks.artist_id
        WHERE lyrics.lyrics_text IS NOT NULL
        GROUP BY artists.name
        HAVING avg_lyric_length IS NOT NULL
        ORDER BY avg_lyric_length DESC;
    """)
    avg_lyric_rows = cur.fetchall()

    # Lyrics length vs chart rank (scatter plot data)
    cur.execute("""
        SELECT 
            LENGTH(lyrics.lyrics_text) AS lyric_length,
            chart_popularity.chart_position
        FROM lyrics
        JOIN tracks ON tracks.id = lyrics.track_id
        JOIN chart_popularity ON chart_popularity.track_id = tracks.id
        WHERE lyrics.lyrics_text IS NOT NULL;
    """)
    scatter_rows = cur.fetchall()

    # Distribution of chart positions (histogram)
    cur.execute("""
        SELECT chart_position
        FROM chart_popularity;
    """)
    chart_positions = [row[0] for row in cur.fetchall()]

    conn.close()

    return avg_rank_rows, avg_lyric_rows, scatter_rows, chart_positions


# 
# Write results to a summary file
# 

def save_summary_file():
    avg_rank_rows, avg_lyric_rows, _, _ = get_calculated_data()

    with open("calculated_results.txt", "w") as f:
        #  Average chart rank 
        f.write("=== Average Chart Rank Per Artist ===\n")
        for artist, avg_rank in avg_rank_rows:
            if avg_rank is None:
                f.write(f"{artist}: No chart data available\n")
            else:
                f.write(f"{artist}: {avg_rank:.2f}\n")

        #  Average lyrics length 
        f.write("\n=== Average Lyrics Length Per Artist ===\n")
        for artist, avg_len in avg_lyric_rows:
            if avg_len is None:
                f.write(f"{artist}: No lyrics data available\n")
            else:
                f.write(f"{artist}: {avg_len:.2f}\n")

    print("Summary file written to calculated_results.txt")


# 
# Run calculations when executed directly
# 

if __name__ == "__main__":
    save_summary_file()
    print("Calculations complete.")
