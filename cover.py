import random
import string
import musicbrainzngs


def download_cover_by_musicbrainz_release_id(release_id: str) -> str:
    cover_art = musicbrainzngs.get_image_front(release_id)
    filename = (
        "".join(random.choices(string.ascii_letters + string.digits, k=6)) + ".jpg"
    )
    with open("./covers/" + filename, "wb") as f:
        f.write(cover_art)
        print("Cover art downloaded!")
    return filename
