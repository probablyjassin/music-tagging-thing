import os

import acoustid
from fuzzywuzzy import fuzz

from config import ACOUSTID_API_KEY, VERBOSE


def detect_audio_from_file(path: str) -> dict:

    matches: list[dict[str, str]] = []
    filename = os.path.basename(path).lower()

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

        if song_title in filename and song_artist in filename:
            return 4  # Priority 1 (highest numerical value for sorting)
        elif song_artist in filename:
            return 3  # Priority 2
        elif song_title in filename:
            return 2  # Priority 3
        else:
            return 1  # Priority 4 (lowest numerical value)

    matches.sort(key=lambda song_dict: get_match_priority(song_dict), reverse=True)

    return matches[0]
