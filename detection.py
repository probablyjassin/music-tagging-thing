import os

from dotenv import load_dotenv

load_dotenv()

import acoustid
from fuzzywuzzy import fuzz

ACOUSTID_API_KEY = os.getenv("ACOUSTID_API_KEY")
if not ACOUSTID_API_KEY:
    raise ValueError("ACOUSTID_API_KEY environment variable not set.")

matches: list[dict] = []

for score, recording_id, title, artist in acoustid.match(
    ACOUSTID_API_KEY, "./YOASOBI.mp3"
):
    print(f"Score: {score}, Title: {title}, Artist: {artist}")
    matches.append({"score": score, "title": title, "artist": artist})

if not matches:
    print("No matches found.")


def get_match_priority(song_dict, search_string):
    song_name = song_dict.get("name", "").lower()
    song_artist = song_dict.get("artist", "").lower()
    search_string_lower = search_string.lower()

    # Use fuzzy matching for more flexible "in" checks
    # You can adjust the threshold (e.g., 80) based on how strict you want the match to be.
    # fuzz.partial_ratio is good for checking if a shorter string is part of a longer one.
    name_in_search = (
        fuzz.partial_ratio(song_name, search_string_lower) > 80
        or song_name in search_string_lower  # Direct check for exact containment
    )
    artist_in_search = (
        fuzz.partial_ratio(song_artist, search_string_lower) > 80
        or song_artist in search_string_lower  # Direct check for exact containment
    )

    if name_in_search and artist_in_search:
        return 4  # Priority 1 (highest numerical value for sorting)
    elif artist_in_search:
        return 3  # Priority 2
    elif name_in_search:
        return 2  # Priority 3
    else:
        return 1  # Priority 4 (lowest numerical value)


good_matches = [match for match in matches if match["score"] > 0.5]
