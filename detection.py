import os
from dotenv import load_dotenv

load_dotenv()

import acoustid
from fuzzywuzzy import fuzz

ACOUSTID_API_KEY = os.getenv("ACOUSTID_API_KEY")
if not ACOUSTID_API_KEY:
    raise ValueError("ACOUSTID_API_KEY environment variable not set.")


def detect_audio_from_file(path: str) -> list[dict]:

    matches: list[dict[str, str]] = []
    filename = os.path.basename(path)

    for _, _, title, artist in acoustid.match(ACOUSTID_API_KEY, path):

        # print(f"Score: {score}, Title: {title}, Artist: {artist}")
        matches.append({"title": title, "artist": artist})

    if not matches:
        print("No matches found.")
        return

    def get_match_priority(song_dict: dict[str, str]):
        song_title = song_dict.get("title", "").lower()
        song_artist = song_dict.get("artist", "").lower()

        # Use fuzzy matching for more flexible "in" checks
        # You can adjust the threshold (e.g., 80) based on how strict you want the match to be.
        # fuzz.partial_ratio is good for checking if a shorter string is part of a longer one.
        name_in_search = (
            fuzz.partial_ratio(song_title, filename) > 80
            or song_title in filename  # Direct check for exact containment
        )
        artist_in_search = (
            fuzz.partial_ratio(song_artist, filename) > 80
            or song_artist in filename  # Direct check for exact containment
        )

        if name_in_search and artist_in_search:
            return 4  # Priority 1 (highest numerical value for sorting)
        elif artist_in_search:
            return 3  # Priority 2
        elif name_in_search:
            return 2  # Priority 3
        else:
            return 1  # Priority 4 (lowest numerical value)

    matches.sort(key=lambda song_dict: get_match_priority(song_dict), reverse=True)

    return matches[0]
