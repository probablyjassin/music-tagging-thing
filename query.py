import os, sys, re
import requests
import musicbrainzngs
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, TCON, APIC, ID3NoHeaderError
from mutagen.mp3 import MP3


musicbrainzngs.set_useragent(
    app="MyMP3Tagger",
    version="1.0",
    contact="your_email@example.com",  # Replace with your email
)


def search_musicbrainz_by_info_or_name(
    title: str | None = None, artist: str | None = None, query: str | None = None
) -> dict | None:

    def get_tags(release: dict) -> dict:
        return {
            "release_id": release["id"],
            "title": release["title"],
            "artist": release["artist-credit"][0]["name"],
            "album": release["release-group"]["title"],
            "year": release["date"].split("-")[0],
            "genre": release["tag-list"][0] if release["tag-list"] else None,
        }

    if not (title and artist):
        query = query.replace("_", " ").replace("-", " ")
        query = re.sub(r"^\d+\s*", "", query)
        query = re.sub(r"\(.*?\)", "", query)
        query = re.sub(r"\[.*?\]", "", query)
        query = re.split(r"\s*[^\w\s]{1,2}\s*", query)
        query = " - ".join(query)

        # Try to split into artist and title using " - " or other likely separators
        if " - " in query:
            parts = query.split(" - ")
        else:
            parts = query.split(" ", 1)  # fallback

        if len(parts) == 2:
            artist = parts[0].strip()
            title = parts[1].strip()
        else:
            artist = None
            title = query.strip()

    print("Searching mp3 tag for...")
    print(f"Title: {title}\nArtist: {artist}")

    try:
        result_candidate = musicbrainzngs.search_releases(
            query=(f'recording:"{title}" AND artist:"{artist}"'),
            limit=5,
        )
        if releases := result_candidate["release-list"]:
            if releases[0]["title"] == title:
                return get_tags(releases[0])
        else:
            print("No result or mismatch, retrying with name and artist reversed...")
            result_candidate = musicbrainzngs.search_releases(
                query=(f'recording:"{artist}" AND artist:"{title}"'),
                limit=5,
            )

            if releases := result_candidate["release-list"]:
                if releases[0]["title"] == title:
                    return get_tags(releases[0])

            return None

    except musicbrainzngs.WebServiceError as e:
        print(f"MusicBrainz API error: {e}")
    return None
