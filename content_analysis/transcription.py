import os
from dotenv import load_dotenv
import assemblyai as aai 

class AudioTranscriber:
    def __init__(self):
        """Load API key from .env file and initialize transcriber."""
        load_dotenv()  # Load environment variables from .env
        self.api_key = os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key not found. Add it to a .env file or set an environment variable.")
        aai.settings.api_key = self.api_key
        self.transcriber = None

    def load_audio(self, file_path):
        """Load an audio file for transcription."""
        config = aai.TranscriptionConfig(disfluencies=True)
        self.transcriber = aai.Transcriber(config=config)
        self.transcript = self.transcriber.transcribe(file_path)

    def print_transcript(self):
        """Print the transcribed text."""
        if not self.transcriber or not hasattr(self, 'transcript'):
            raise ValueError("No transcription found. Use load_audio() first.")
        if self.transcript.status == aai.TranscriptStatus.error:
            print(f"Error: {self.transcript.error}")
        else:
            return self.transcript.text
        
    def transcribe(self, audio_path):
        self.load_audio(audio_path)
        return self.print_transcript()




