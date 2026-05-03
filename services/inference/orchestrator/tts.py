import subprocess


class TTS:
    def speak(self, text):
        output_file = "output.wav"

        subprocess.run([
            "espeak",
            "-w", output_file,
            text
        ])

        with open(output_file, "rb") as f:
            return f.read()