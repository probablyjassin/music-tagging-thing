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
