# gather_genius.py

import sqlite3
from genius_api import search_genius_song
from db_setup import DB_NAME

SONGS = [
    ("Mariah Carey", "All I Want For Christmas Is You"),
    ("Wham!", "Last Christmas"),
    ("Brenda Lee", "Rockin' Around the Christmas Tree"),
    ("Bobby Helms", "Jingle Bell Rock"),
    ("HUNTR/X", "Golden"),
    ("Taylor Swift", "The Fate Of Ophelia"),
    ("Alex Warren", "Ordinary"),
    ("Ariana Grande", "Santa Tell Me"),
    ("Nat King Cole", "The Christmas Song"),
    ("Andy Williams", "It's The Most Wonderful Time Of The Year"),

    ("Kelly Clarkson", "Underneath the Tree"),
    ("Olivia Dean", "Man I Need"),
    ("Dean Martin", "Let It Snow! Let It Snow! Let It Snow!"),
    ("Michael Bublé", "It's Beginning to Look a Lot Like Christmas"),
    ("The Ronettes", "Sleigh Ride"),

    ("Burl Ives", "A Holly Jolly Christmas"),
    ("José Feliciano", "Feliz Navidad"),
    ("Darlene Love", "Christmas (Baby Please Come Home)"),
    ("Bing Crosby", "White Christmas"),
    ("Leon Thomas", "Mutt"),

    ("Frank Sinatra", "Jingle Bells"),
    ("Chuck Berry", "Run Rudolph Run"),
    ("Perry Como", "It's Beginning To Look A Lot Like Christmas"),
    ("Taylor Swift", "Opalite"),
    ("Kehlani", "Folded"),
    
    ("Ella Langley", "Choosin' Texas"),
    ("Justin Bieber", "Daisies"),
    ("Eartha Kitt", "Santa Baby"),
    ("Elvis Presley", "Blue Christmas"),
    ("Jonas Brothers", "Like It's Christmas"),
    ("Michael Buble", "Holly Jolly Christmas"),
    ("Gene Autry& The Pinafores", "Rudolph The Red-Nosed Reindeer"),
    ("Vince Guaraldi Trio", "Christmastime Is Here"),
    ("The Beach Boys", "Little Saint Nick"),
    ("Kelly Clarkson&Ariana Grande", "Santa, Can't You Hear Me"),
    ("Thurl Ravenscroft", "You're A Mean One, Mr. Grinch"),
    ("Chris BrownFeaturingBryson Tiller", "It Depends"),
    ("Ed Sheeran&Elton John", "Merry Christmas"),
    ("Justin Bieber", "Mistletoe"),
    ("Tate McRae", "Tit For Tat"),
    ("Jackson 5", "Santa Claus Is Comin' To Town"),
    ("Olivia Dean", "So Easy (To Fall In Love)"),
    ("Dean Martin", "Baby It's Cold Outside"),
    ("Darlene Love", "Winter Wonderland"),
    ("Donny Hathaway", "This Christmas"),
    ("Sabrina Carpenter", "Tears"),
    ("Riley GreenFeaturing Ella Langley", "Don't Mind If I Do"),
    ("RAYE", "Where Is My Husband!"),
    ("GunnaFeaturingBurna Boy", "wgft"),
    ("KATSEYE", "Gabriela"),
    ("Russell Dickerson", "Happen To Me"),
    ("Morgan Wallen", "20 Cigarettes"),
    ("Myles Smith", "Nice To Meet You"),
    ("Megan Moroney", "6 Months Later"),
    ("Mariah The Scientist&Kali Uchis", "Is It A Crime"),
    ("Justin Bieber", "Yukon"),
    ("BigXthaPlug Featuring Ella Langley", "Hell At Night"),
    ("Hudson Westbrook", "House Again"),
    ("Max McNown", "Better Me For You (Brown Eyes)"),
    ("Olivia Dean", "A Couple Minutes"),
    ("Tate McRae", "Nobody's Girl"),
    ("YoungBoy Never Broke Again", "Shot Callin"),
    ("Taylor Swift", "Elizabeth Taylor"),
    ("Tucker Wetmore", "3,2,1"),
    ("Tame Impala", "Dracula"),
    ("Metro Boomin,Quavo, Breskii & YKNIECE", "Take Me Thru Dere"),
    ("Cody Johnson", "The Fall"),
    ("Cody Johnson", "Travelin' Soldier"),
    ("Tyler, The Creator", "Sugar On My Tongue"),
    ("sombr", "12 To 12"),
    ("Chase Matthew", "Darlin'"),
    ("Shaboozey&Jelly Roll", "Amen"),
    ("Gavin Adcock", "Last One To Know"),
    ("HARDY", "Favorite Country Song"),
    ("Taylor Swift", "Father Figure"),
    ("Ed Sheeran", "Camera"),
    ("Cardi B", "ErrTime"),
    ("Luke Combs", "Back In The Saddle"),
    ("Taylor Swift", "Wi$h Li$t"),
    ("Parmalee", "Cowgirl"),
    ("Gwen Stefani", "Shake The Snow Globe"),
    ("Luke Combs", "Days Like These"),
    ("Tate McRae", "Anything But Love"),
    ("Parker McCollum", "What Kinda Man"),
    ("Jason Aldean", "How Far Does A Goodbye Go"),
    ("Olivia Dean", "Nice To Each Other"),
    ("David Guetta,Teddy Swims&Tones And I", "Gone Gone Gone"),
    ("Lady Gaga", "The Dead Dance"),
    ("G Herbo", "Went Legit"),
    ("The Marias", "Sienna"),
    ("Cynthia Erivo&Ariana Grande", "For Good"),
    ("Cynthia Erivo", "No Good Deed"),
    ("Olivia Dean", "Let Alone The One You Love"),
    ("Taylor SwiftFeaturingSabrina Carpenter", "The Life Of A Showgirl"),
    ("Sabrina Carpenter", "When Did You Get Hot?"),
]
def track_exists(conn, artist_name, title):
    cur = conn.cursor()
    cur.execute("""
        SELECT tracks.id
        FROM tracks
        JOIN artists ON tracks.artist_id = artists.id
        WHERE artists.name = ? AND tracks.title = ?
    """, (artist_name, title))
    row = cur.fetchone()
    return row is not None


def add_song_to_db(conn, artist_name, title):
    cur = conn.cursor()

    # 1. ensure artist exists
    cur.execute("INSERT OR IGNORE INTO artists (name) VALUES (?)", (artist_name,))
    cur.execute("SELECT id FROM artists WHERE name = ?", (artist_name,))
    row = cur.fetchone()
    if not row:
        print(" Could not get artist id for", artist_name)
        return False
    artist_id = row[0]

    # 2. call Genius API
    search_term = f"{artist_name} {title}"
    result = search_genius_song(search_term)
    if not result:
        print(" No Genius result for", search_term)
        return False

    genius_id = result.get("id")

    # 3. insert track if new
    cur.execute("""
        INSERT OR IGNORE INTO tracks (artist_id, title, genius_song_id)
        VALUES (?, ?, ?)
    """, (artist_id, title, genius_id))

    if cur.rowcount == 0:
        # nothing inserted (already in DB)
        print("Already had:", artist_name, "-", title)
        return False

    print(" Saved:", artist_name, "-", title)
    return True


def get_track_count():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tracks")
    count = cur.fetchone()[0]
    conn.close()
    return count


if __name__ == "__main__":
    BATCH_LIMIT = 25   # max new tracks per run
    TARGET_TOTAL = 100 # stop once we reach this many

    current = get_track_count()
    print("Current tracks in DB:", current)

    if current >= TARGET_TOTAL:
        print(" Already reached target of", TARGET_TOTAL)
    else:
        conn = sqlite3.connect(DB_NAME)
        new_added = 0

        for artist, title in SONGS:
            if new_added >= BATCH_LIMIT:
                break

            # skip if already in DB
            if track_exists(conn, artist, title):
                print("Skipping existing:", artist, "-", title)
                continue

            # try to add
            inserted = add_song_to_db(conn, artist, title)
            if inserted:
                new_added += 1
                current += 1
                if current >= TARGET_TOTAL:
                    print(" Reached target of", TARGET_TOTAL, "tracks.")
                    break

        conn.commit()
        conn.close()

        print("New tracks added this run:", new_added)
        print("Total tracks now (approx):", current)