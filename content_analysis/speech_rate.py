import librosa
import numpy as np
from g4f.client import Client
from transcription import AudioTranscriber
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def get_speech_duration(audio_path, threshold=0.003, frame_length=2048, hop_length=512):
    y, sr = librosa.load(audio_path, sr=None)  # Load audio file
    energy = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

    # Convert to boolean speech detection (True where energy is above threshold)
    speech_frames = energy > threshold

    # Calculate total speech duration
    total_speech_time = np.sum(speech_frames) * (hop_length / sr)  # Convert frames to seconds
    return total_speech_time

def calc_speech_rate(speech_duration,transcript):
    speech_duration=speech_duration/60
    no_of_words=len(transcript.split())
    print(f"Number of words: {no_of_words} words")
    speech_rate=no_of_words/speech_duration
    print(f"Speech rate: {speech_rate:.2f} wpm")
    return speech_rate

def speech_rate_score(speech_rate, optimal=142, sigma=60, min_score=0.2):
    # ideal speech rate for interviews: 125-160 wpm
    score=np.exp(-((speech_rate - optimal) / sigma) ** 2) # gaussian scoring
    return max(score, min_score)*100

def report_generation(transcript,speech_duration,speech_rate,speech_score):
    prompt = "'{text}'\n the above is a transcript from a mock interview that received a score of '{num}' for speech rate. The duration of this transcript was {time} and had a speech rate of {wpm} wpm.\nYou are an expert on interviews. Analyze the above transcript critically, assuming the ideal speech rate for interviews is 125-160 wpm, and provide helpful, actionable tips on how the user can manage their speech and thus improve their score.\n answer format: \n'what you did right:' followed by a brief bulleted list of things the user did right \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \neach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.format(text=transcript, num=speech_score, time=speech_duration, wpm=speech_rate)}],
    )
    
    # Capture the response text and split into keywords
    #print(prompt)
    result = response.choices[0].message.content
    return result

def main():
    audio_path = r"1_audio\aud_1.wav"
    a = AudioTranscriber()
    transcript=a.transcribe(audio_path)
    speech_duration = get_speech_duration(audio_path)
    print(f"Speech duration: {speech_duration:.2f} seconds")
    speech_rate = calc_speech_rate(speech_duration, transcript)
    score = speech_rate_score(speech_rate)
    print(f"Speech rate score: {score:.2f}%")
    report = report_generation(transcript, speech_duration, speech_rate, speech_rate_score)
    print("\n\nREPORT:\n\n", report)
main()