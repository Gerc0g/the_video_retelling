import whisper
import time
import numpy as np
import os


class Transcriber:
    def __init__(self, model_size='base'):
        self.model = whisper.load_model(model_size)
        self.json_result = {'lang' : None,
                           'text' : None,
                           'timeout': None,
                           'type': None
                           }

    def transcribe(self, audio_path):
        start_time = time.time()

        if isinstance(audio_path, str):
            audio = whisper.load_audio(audio_path)
            self.json_result['type'] = 'Audio to Text'
        elif isinstance(audio_path, os.PathLike):
            audio = whisper.load_audio(audio_path)
            self.json_result['type'] = 'Video to Audio to Text'
        else:
            raise ValueError("audio_input должен быть либо путем к файлу, либо объектом os.PathLike")

        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)

        _, probs = self.model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        self.json_result['lang'] = detected_language

        options = whisper.DecodingOptions()
        result = whisper.decode(self.model, mel, options)
        self.json_result['text'] = result.text

        self.json_result['timeout'] = str(time.time() - start_time)

        return self.json_result