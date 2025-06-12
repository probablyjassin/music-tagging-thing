import os
from pydub import AudioSegment

from detection import detect_audio_from_file

for root, dirs, files in os.walk("./input"):
    for file in files:
        source_file_path = os.path.join(root, file)
        mp3_file_name = f"{file.rsplit(sep='.', maxsplit=1)[0]}.mp3"
        source_audio: AudioSegment = AudioSegment.from_file(source_file_path)
        source_audio.export(f"./output/{mp3_file_name}", format="mp3")

        best_audio_match = detect_audio_from_file(f"./output/{mp3_file_name}")

        print(best_audio_match)
