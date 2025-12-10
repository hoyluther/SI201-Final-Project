# lyrics_api.py
# Simple wrapper for lyrics.ovh API

import requests

BASE_URL = "https://api.lyrics.ovh/v1"

def get_lyrics(artist, title):
    """
    Input:  artist (string), title (string)
    Output: lyrics text (string) OR None
    """
    url = f"{BASE_URL}/{artist}/{title}"

    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        lyrics = data.get("lyrics")
        if not lyrics:
            print(f"⚠️ No lyrics found for {artist} - {title}")
            return None
        return lyrics
    except requests.exceptions.RequestException as e:
        print(f"❌ Lyrics.ovh error for {artist} - {title}: {e}")
        return None