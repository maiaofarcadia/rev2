import asyncio # (UNCOMMENT THIS LINE WHEN RUNNING LOCALLY)
from g4f.client import Client
import time
from transcription import AudioTranscriber

# Fix Windows event loop issue (UNCOMMENT THIS LINE WHEN RUNNING LOCALLY)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

with open(r"..\questions.txt", "r", encoding="utf-8") as file:
    questions = [line.strip() for line in file if line.strip()]

def answer_relevance(transcript,question):
    prompt = "'{ans}'\n The above is a transcript of a response from a mock interview. The question asked was: '{que}'.\nYou are an expert on interviews. Analyze the above transcript critically and strictly, and return a score for the response's relevance (0-not relevant at all, 100-perfect relevance). Return only the score as an integer value, with no text before or after the score."
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.format(ans=transcript, que=question)}],
    )
    
    # Capture the response text and split into keywords
    result = response.choices[0].message.content
    return result

def report_generate(score, transcript, question):
    prompt = "'{text}'\n the above is a transcript from a mock interview that received a score of '{num}'. The question asked was: '{que}'.\nYou are an expert on interviews. Analyze the above transcript critically, and provide helpful, actionable tips on how the user can improve their response's relevance to the question and thus their score.\n answer format: \n'what you did right:' followed by a brief bulleted list of things the user did right \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \neach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.format(text=transcript, num=score,que=question)}],
    )
    
    # Capture the response text and split into keywords
    #print(prompt)
    result = response.choices[0].message.content
    return result

def main():
    start_time = time.time()  # Record start time
    # ADD CODE TO RUN NEW.PY TEST (NOT FOR THIS REVIEW), STORE QUESTION (DONE), READ AUDIO FILE (DONE), GET TRANSCRIPT(DONE), AND STORE AS TEXT (DONE)
    question=questions[0]
    audio_path = r"..\1_audio\aud_1.wav"
    a = AudioTranscriber()
    transcript=a.transcribe(audio_path)
    score=answer_relevance(transcript,question)
    print("answer relevance score: ", score)
    report=report_generate(score, transcript, question)
    # CALL THE REPORT SCREEN GENERATION FUNCTION (IF WE'RE MAKING ONE)
    print("\n\nREPORT:\n\n", report) # PUT THIS TEXT IN THE REPORT SCREEN (IF WE'RE MAKING ONE)
    end_time = time.time()  # Record end time
    execution_time = end_time - start_time  # Calculate execution time
    print(f"\nExecution Time: {execution_time} seconds") #WILL BE LONGER LOCALLY

main()