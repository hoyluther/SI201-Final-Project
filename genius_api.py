import os
import requests

def search_genius_song(search_term):
    token = os.environ.get("GENIUS_TOKEN")
    print("DEBUG GENIUS_TOKEN in function =", repr(token))  # don't paste this output online

    if not token:
        print("GENIUS_TOKEN not set inside Python.")
        return None

    url = "https://api.genius.com/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": search_term}

    try:
        resp = requests.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("response", {}).get("hits", [])
        if not hits:
            print("No Genius results.")
            return None
        first = hits[0]["result"]
        print("Genius search worked:")
        print(first.get("title"), "-", first.get("artist_names"))
        print(first.get("url"))
        return first
    except requests.exceptions.RequestException as e:
        print("Genius error:", e)
        return None


if __name__ == "__main__":
    print("GENIUS_TOKEN at top-level =", repr(os.environ.get("GENIUS_TOKEN")))
    search_genius_song("Imagine Dragons Believer")