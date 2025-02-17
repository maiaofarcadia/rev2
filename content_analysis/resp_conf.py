import asyncio # (UNCOMMENT THIS LINE WHEN RUNNING LOCALLY)
from g4f.client import Client
import time
from transcription import AudioTranscriber

# Fix Windows event loop issue (UNCOMMENT THIS LINE WHEN RUNNING LOCALLY)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def response_confidence(transcript):
    prompt = "'{text}'\n the above is a transcript from a mock interview. You are an expert on interviews. Analyze the above transcript critically and strictly, and return a score for the response's confidence (0-not confident at all, 100-perfect confidence). Return only the score as an integer value, with no text before or after the score."
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.format(text=transcript)}],
    )
    
    # Capture the response text and split into keywords
    result = response.choices[0].message.content
    return result

def report_generate(score, transcript):
    prompt = "'{text}'\n the above is a transcript from a mock interview that received a score of '{num}'. You are an expert on interviews. Analyze the above transcript critically, and provide helpful, actionable tips on how the user can improve their response's confidence and thus their score.\n answer format: \n'what you did right:' followed by a brief bulleted list of things the user did right \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely in each tip what the user can improve, why it's relevant to confidence (from an interview standpoint), and how the user can improve it. \neach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.format(text=transcript, num=score)}],
    )
    
    # Capture the response text and split into keywords
    #print(prompt)
    result = response.choices[0].message.content
    return result

def main():
    start_time = time.time()  # Record start time
    #ADD CODE TO RUN NEW.PY TEST, READ AUDIO FILE, GET TRANSCRIPT, AND STORE AS TEXT
    audio_path = r"..\1_audio\aud_1.wav"
    a = AudioTranscriber()
    transcript=a.transcribe(audio_path)
    score=response_confidence(transcript)
    print("response confidence score: ", score)
    report=report_generate(score, transcript)
    # CALL THE REPORT SCREEN GENERATION FUNCTION (IF WE'RE MAKING ONE)
    print("\n\nREPORT:\n\n", report) #PUT THIS TEXT IN THE REPORT SCREEN (IF WE'RE MAKING ONE)
    end_time = time.time()  # Record end time
    execution_time = end_time - start_time  # Calculate execution time
    print(f"\nExecution Time: {execution_time} seconds") # WILL BE LONGER LOCALLY

main()