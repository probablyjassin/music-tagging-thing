import os

import acoustid
from fuzzywuzzy import fuzz

from config import ACOUSTID_API_KEY, VERBOSE


def detect_audio_from_file(path: str) -> dict:

    matches: list[dict[str, str]] = []
    filename = os.path.basename(path)

    if VERBOSE:
        print(f"Trying to match the audio in {path}...")

    for _, _, title, artist in acoustid.match(ACOUSTID_API_KEY, path):
        matches.append({"title": title, "artist": artist})

    if VERBOSE:
        print(f"{len(matches)} potential matches found")

    if not matches:
        print("No pure audio matches found.")
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
