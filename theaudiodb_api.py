# theaudiodb_api.py
import requests

BASE_URL = "https://theaudiodb.com/api/v1/json/2"

def get_track_details(track_name):
    """
    Safely fetch track data from TheAudioDB.
    Returns a track dict or None.
    Never crashes on bad responses.
    """

    url = f"{BASE_URL}/searchtrack.php"
    params = {"t": track_name}

    try:
        resp = requests.get(url, params=params, timeout=8)
    except requests.exceptions.RequestException as e:
        print(f" AudioDB request error for '{track_name}': {e}")
        return None

    # Handle non-200 status codes cleanly
    if resp.status_code != 200:
        print(f" AudioDB HTTP {resp.status_code} for '{track_name}'")
        return None

    # Try parsing JSON safely
    try:
        data = resp.json()
    except Exception:
        print(f" AudioDB returned non-JSON for '{track_name}'")
        print("      Raw response preview:", resp.text[:200])
        return None

    # Expected format: {"track": [ {...} ] }
    tracks = data.get("track")
    if not tracks:
        print(f" AudioDB returned no results for '{track_name}'")
        return None

    return tracks[0]  # First match is usually best
