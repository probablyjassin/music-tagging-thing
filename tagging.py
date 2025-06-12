import os
import requests
import musicbrainzngs
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, TCON, APIC, ID3NoHeaderError
from mutagen.mp3 import MP3

# --- Configuration ---
# MusicBrainz application name and version (recommended for API usage)
musicbrainzngs.set_useragent(
    app="MyMP3Tagger",
    version="1.0",
    contact="your_email@example.com",  # Replace with your email
)


def search_musicbrainz(title: str, artist: str) -> dict | None:
    """
    Searches MusicBrainz for a track by title and artist.

    Args:
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        dict or None: A dictionary containing track details if found, otherwise None.
    """
    print(f"Searching MusicBrainz for '{title}' by '{artist}'...")
    try:
        # Search for recordings (tracks)
        result = musicbrainzngs.search_recordings(
            query=f"{title} {artist}",  # Combined query for better results
            artist=artist,  # Specific artist filter
            title=title,  # Specific title filter
            strict=True,  # Make search more strict
            limit=5,  # Limit results
        )

        if not result["recording-list"]:
            print("No recordings found.")
            return None

        # Iterate through recordings to find a good match and get release group info
        for recording in result["recording-list"]:
            # Prioritize recordings that have an associated release (album)
            if "releases" in recording and recording["releases"]:
                release = recording["releases"][0]  # Take the first release

                # Check for artists and their names
                recording_artists = [
                    art["artist"]["name"]
                    for art in recording.get("artist-credit", [])
                    if "artist" in art
                ]

                # Basic sanity check for artist match
                if any(artist.lower() in ra.lower() for ra in recording_artists):
                    print(
                        f"Found recording: {recording['title']} by {', '.join(recording_artists)}"
                    )

                    # Try to get the release group (album info) for more details
                    if "release-group-id" in release:
                        release_group_id = release["release-group-id"]
                        print(f"Fetching release group for ID: {release_group_id}")
                        release_group = musicbrainzngs.get_release_group_by_id(
                            release_group_id,
                            includes=["artist-credits", "releases", "url-rels"],
                        )

                        album_title = release_group["release-group"]["title"]
                        album_year = None
                        if "first-release-date" in release_group["release-group"]:
                            album_year = release_group["release-group"][
                                "first-release-date"
                            ].split("-")[
                                0
                            ]  # Get just the year

                        cover_art_url = None
                        # MusicBrainz links to Cover Art Archive
                        for rel in release_group["release-group"].get("url-rels", []):
                            if rel["type"] == "cover art" and "resource" in rel:
                                cover_art_url = (
                                    rel["resource"] + "/front"
                                )  # Get front cover
                                break

                        # Fallback for cover art from individual releases if available
                        if not cover_art_url and release.get("id"):
                            try:
                                release_details = musicbrainzngs.get_release_by_id(
                                    release["id"], includes=["url-rels"]
                                )
                                for rel in release_details["release"].get(
                                    "url-rels", []
                                ):
                                    if rel["type"] == "cover art" and "resource" in rel:
                                        cover_art_url = rel["resource"] + "/front"
                                        break
                            except Exception as e:
                                print(
                                    f"Could not get release details for cover art: {e}"
                                )

                        return {
                            "title": recording["title"],
                            "artist": ", ".join(recording_artists),
                            "album": album_title,
                            "year": album_year,
                            "cover_art_url": cover_art_url,
                        }
                    else:
                        print("Recording has no associated release group.")
            else:
                print(
                    f"Skipping recording '{recording['title']}' as it has no releases."
                )
    except musicbrainzngs.WebServiceError as e:
        print(f"MusicBrainz API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during MusicBrainz search: {e}")
    return None


def download_cover_art(url, output_path="cover_art.jpg"):
    """
    Downloads an image from a URL.

    Args:
        url (str): The URL of the image.
        output_path (str): The path to save the image.

    Returns:
        str or None: The path to the downloaded image if successful, otherwise None.
    """
    if not url:
        return None
    print(f"Downloading cover art from: {url}")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        with open(output_path, "wb") as out_file:
            for chunk in response.iter_content(chunk_size=8192):
                out_file.write(chunk)
        print(f"Cover art downloaded to: {output_path}")
        return output_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading cover art: {e}")
    return None


def tag_mp3_file(mp3_filepath, metadata, cover_art_path=None):
    """
    Tags an MP3 file with provided metadata and cover art.

    Args:
        mp3_filepath (str): The path to the MP3 file.
        metadata (dict): A dictionary containing 'title', 'artist', 'album', 'year'.
        cover_art_path (str, optional): Path to the cover art image file.
    """
    try:
        # Load the MP3 file. If no ID3 header, one will be created.
        audio = MP3(mp3_filepath)
        if not audio.tags:
            audio.add_tags()

        # Set ID3 tags
        if metadata.get("title"):
            audio.tags.add(TIT2(encoding=3, text=[metadata["title"]]))  # Title
        if metadata.get("artist"):
            audio.tags.add(TPE1(encoding=3, text=[metadata["artist"]]))  # Artist
        if metadata.get("album"):
            audio.tags.add(TALB(encoding=3, text=[metadata["album"]]))  # Album
        if metadata.get("year"):
            audio.tags.add(
                TDRC(encoding=3, text=[metadata["year"]])
            )  # Year (Recording Date)

        # Add cover art
        if cover_art_path and os.path.exists(cover_art_path):
            try:
                with open(cover_art_path, "rb") as f:
                    audio.tags.add(
                        APIC(
                            encoding=3,  # UTF-8
                            mime="image/jpeg",  # Adjust if not JPEG
                            type=3,  # 3 is for Front Cover
                            desc="Cover",
                            data=f.read(),
                        )
                    )
                print(f"Added cover art to {mp3_filepath}")
            except Exception as e:
                print(f"Error adding cover art to ID3 tags: {e}")
        else:
            print("No cover art path provided or file does not exist.")

        # Save the changes
        audio.save()
        print(f"Successfully tagged {mp3_filepath}")

    except ID3NoHeaderError:
        print(f"No ID3 header found in {mp3_filepath}. A new one will be created.")
        # Mutagen should handle this, but it's good to be aware.
    except Exception as e:
        print(f"Error tagging MP3 file {mp3_filepath}: {e}")


if __name__ == "__main__":
    # Example usage:
    # You would get these from your song identification step
    known_title = "夜に駆ける"
    known_artist = "Queen"
    mp3_file_to_tag = (
        "path/to/your/song.mp3"  # !!! CHANGE THIS TO YOUR ACTUAL MP3 FILE PATH !!!
    )

    if not os.path.exists(mp3_file_to_tag):
        print(f"Error: MP3 file not found at {mp3_file_to_tag}")
        exit()

    print(
        f"Attempting to tag '{mp3_file_to_tag}' with info for '{known_title}' by '{known_artist}'"
    )

    # 1. Search MusicBrainz for detailed metadata
    metadata = search_musicbrainz(known_title, known_artist)

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
