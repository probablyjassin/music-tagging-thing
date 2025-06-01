import os
from pydub import AudioSegment

for root, dirs, files in os.walk("./input"):
    for file in files:
        source_file_path = os.path.join(root, file)
        print(source_file_path)
        mp3_file_name = f"{file.rsplit(sep='.', maxsplit=1)[0]}.mp3"
        print(mp3_file_name)
        source_audio = AudioSegment.from_file(source_file_path)
        source_audio.export(f"./output/{mp3_file_name}", format="mp3")
        print("Done!")


# add metadata

# convert file type
