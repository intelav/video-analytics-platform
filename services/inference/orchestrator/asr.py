from faster_whisper import WhisperModel


class ASR:
    def __init__(self):
        self.model = WhisperModel("base", compute_type="int8")

    def transcribe(self, audio_path):
        segments, _ = self.model.transcribe(audio_path)
        return " ".join([seg.text for seg in segments])