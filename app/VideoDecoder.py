from moviepy.editor import VideoFileClip
import tempfile
import time

class VideoToAudioConverter:
    def __init__(self):
        self.json_result = {'path' : None,
                           'timeout' : None
                           }

    def extract_audio(self, video_file):
        start_time = time.time()

        # Извлекаем аудио из видео файла
        video_clip = VideoFileClip(video_file)
        audio_clip = video_clip.audio

        # Сохраняем аудио во временный файл в формате WAV
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio_clip.write_audiofile(temp_file.name, codec='pcm_s16le', fps=44100, verbose=False)

        temp_file.close()

        # Освобождаем ресурсы
        audio_clip.close()
        video_clip.close()

        self.json_result['path'] = temp_file.name

        self.json_result['timeout'] = str(time.time() - start_time)

        return self.json_result
