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
            "date": release["date"],
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


def download_cover_art(url, output_path="cover_art.jpg"):
    """cover_art = musicbrainzngs.get_image_front(release_id)
    with open(f"{title}.jpg", "wb") as f:
        f.write(cover_art)
        print("Cover art downloaded!")"""


if __name__ == "__main__":
    # if not os.path.exists(mp3_file_to_tag):
    #    print(f"Error: MP3 file not found at {mp3_file_to_tag}")
    #    exit()

    # 1. Search MusicBrainz for detailed metadata
    # result = search_musicbrainz(known_title, known_artist)
    result = search_musicbrainz_by_info_or_name(query="可不 ⧸ 着包み [WNQNCJgJOmg]")
    print(result)
    sys.exit(0)

    cover_art_filepath = None
    if metadata and metadata.get("cover_art_url"):
        # 2. Download cover art if available
        cover_art_filepath = download_cover_art(
            metadata["cover_art_url"], "temp_cover.jpg"
        )
    else:
        print("No cover art URL found or metadata not retrieved.")

    if metadata:
        # 3. Tag the MP3 file
        tag_mp3_file(mp3_file_to_tag, metadata, cover_art_filepath)
    else:
        print("Could not retrieve full metadata. MP3 file not tagged.")

    # Clean up downloaded cover art
    if cover_art_filepath and os.path.exists(cover_art_filepath):
        try:
            os.remove(cover_art_filepath)
            print(f"Cleaned up temporary cover art file: {cover_art_filepath}")
        except Exception as e:
            print(f"Error removing temporary cover art file: {e}")
