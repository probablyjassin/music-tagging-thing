import os
from pydub import AudioSegment

from detection import detect_audio_from_file
from query import search_musicbrainz_by_info_or_name
from cover import download_cover_by_musicbrainz_release_id
from tagging import tag_mp3_file

from config import VERBOSE

print("Begin processing files in ./input...")

for root, dirs, files in os.walk("./input"):
    for file in files:
        source_file_path = os.path.join(root, file)

        print(f"Found {source_file_path}")

        mp3_file_name = f"{file.rsplit(sep='.', maxsplit=1)[0]}.mp3"
        source_audio: AudioSegment = AudioSegment.from_file(source_file_path)
        source_audio.export(f"./output/{mp3_file_name}", format="mp3")

        print("Converted to MP3\nSearching for fitting tagging...")

        best_audio_match = detect_audio_from_file(f"./output/{mp3_file_name}")

        if VERBOSE:
            print("Best match by mp3 audio:")
            print(best_audio_match)

        title = None
        artist = None
        query = None
        if best_audio_match:
            title = best_audio_match["title"]
            artist = best_audio_match["artist"]
        else:
            query = mp3_file_name
        tag_result = search_musicbrainz_by_info_or_name(title, artist, query)

        if VERBOSE:
            print(
                f"Searched tag Result by: Title: {title}, Artist: {artist}, Query: {query}..."
            )
            print(tag_result)

        cover_filename = None
        if tag_result:
            try:
                cover_filename = download_cover_by_musicbrainz_release_id(
                    tag_result["release_id"]
                )

                tag_mp3_file(
                    f"./output/{mp3_file_name}",
                    tag_result,
                    cover_art_path=f"./covers/{cover_filename}",
                )
            except:
                print("Error fetchig cover image - skipping")
        else:
            print(f"No results found for {source_file_path}. Won't tag.")
