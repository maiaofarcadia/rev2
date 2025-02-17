from g4f.client import Client
import time
import ast
from transcription import AudioTranscriber
import asyncio
from asyncio import WindowsSelectorEventLoopPolicy

# Set the event loop policy to avoid the warning
asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())


def filler_jargon(transcript):
    prompt = "'{ans}'\n the above is a transcript of a response from a mock interview. You are an expert on interviews. Analyze the above transcript critically and strictly, and return a list of filler words (for example, words such as um, uh, hm, okay, like, you know, so, kind of, etc) and a list of jargon words separately. Ensure that you return ONLY the 2 lists in the format of ['word1', 'word2',...], 1 list in 1 line, with no empty lines between them, and with no text before or after the lists."
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.format(ans=transcript)}],
    )
    # Capture the response text and split into keywords
    result = response.choices[0].message.content
    print(result)
    # Split the string into two lines
    lines = result.split("\n")
    # Convert each line from string representation to an actual list
    filler_words = ast.literal_eval(lines[0])
    jargon_words = ast.literal_eval(lines[1])
    # print("Filler Words:", filler_words, type(filler_words))
    # print("Jargon Words:", jargon_words, type(jargon_words))
    return filler_words,jargon_words

def calc_filler_jargon_score(transcript, filler_count, jargon_count):
    total_words = max(len(transcript.split()), 1)  # Avoid division by zero
    # Set an acceptable jargon threshold (e.g., 5% of the total words)
    max_allowed_jargon = total_words * 0.1
    excess_jargon = max(0, jargon_count - max_allowed_jargon)  # Only penalize excess jargon
    # Compute weighted penalties
    filler_penalty = filler_count * 2  # Filler words are more harmful
    jargon_penalty = excess_jargon * 0.75  # Jargon is allowed in moderation
    # Calculate total penalty
    penalty = (filler_penalty + jargon_penalty) / total_words
    score = max(10, 100 - (penalty * 150))  # Scale appropriately
    return score

def report_generate(score, transcript, filler_words, jargon_words):
    fw=str(filler_words)
    jw=str(jargon_words)
    prompt = "'{text}'\n the above is a transcript from a mock interview that received a score of '{num}' for jargon and filler word analysis.\njargon words identified: {jargon}\nfiller words identified={filler}\nYou are an expert on interviews. Analyze the above transcript critically, and provide helpful, actionable tips on how the user can reduce filler word and jargon usage in their responses and thus improve their score.\n answer format: \n'what you did right:' followed by a brief bulleted list of things the user did right \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \neach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
    client = Client()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt.format(text=transcript, num=score,filler=fw,jargon=jw)}],
    )
    # Capture the response text and split into keywords
    #print(prompt)
    result = response.choices[0].message.content
    return result

def main():
    # transcript="H-hi, I'm Anirudh, nice to uh meet you. I hope we'll like, work well together. Given my um, experience in full-stack development, I'm kind of proficient in leveraging you know, asynchronous microservices architecture, optimizing RESTful API endpoints, and hmm, implementing scalable CI/CD pipelines for automated deployments."
    #transcript2="Hi, I'm Anirudh, nice to meet you. I look forward to working together. I have experience in full-stack development and specialize in building efficient, reliable web applications. I focus on improving system performance, designing well-structured APIs, and automating deployment processes to ensure smooth operations."
    audio_path = r"1_audio\aud_1.wav"
    a = AudioTranscriber()
    transcript=a.transcribe(audio_path)
    filler_words,jargon_words=filler_jargon(transcript)
    print("filler words: ",filler_words,"\n jargon words: ",jargon_words)
    #print(len(transcript.split()),len(filler_words),len(jargon_words))
    score=calc_filler_jargon_score(transcript,len(filler_words),len(jargon_words))
    print(f"filler/jargon analysis score: {score:.2f}%")
    report=report_generate(score, transcript,filler_words,jargon_words)
    print("\n\nREPORT:\n\n", report)

main()