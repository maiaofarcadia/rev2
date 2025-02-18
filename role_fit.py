from g4f.client import Client
from new import VideoRecorderApp
import customtkinter as ctk
from content_analysis.transcription import AudioTranscriber
import time
import asyncio
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class RoleFit:
    def __init__(self):
        self.client = Client()
        self.job_desc = ""

    def create_test_q(self, num_q=1):
        self.job_desc = input("Paste your job description: \n\n")
        prompt = """'{text}'\n the above is a job description.\nYou are an expert on interviews. Analyze the above job description and provide '{num}' interview question(s) aimed at analyzing if the user is a good fit for the given role. Reply only with 1 question in each line, with no empty lines between them, no text before or after the question(s), and no bullet point indicators before the question (eg. '1.'). Do not reply in markdown format, just give me clean text with points"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.format(text=self.job_desc, num=num_q)}],
        )
        
        result = response.choices[0].message.content
        
        with open("role_fit_q.txt", "w", encoding="utf-8") as file:
            file.write(result)

    def role_fit_score(self, transcript):
        prompt = """'{ans}'\n the above is a transcript of a response from a mock interview aimed at identifying how well the user fits a given role. The job description is as follows:\n '{jd}'.\nYou are an expert on interviews. Analyze the above transcript critically and strictly, and return a score for how well the user fits the role (0-not suited at all, 100-perfect suitability). Return only the score as an integer value, with no text before or after the score."""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.format(ans=transcript, jd=self.job_desc)}],
        )
        
        result = response.choices[0].message.content
        return int(result)

    def report_gen(self, transcript, score):
        prompt = """'{text}'\n the above is a transcript from a mock interview aimed at discerning how suitable the user was at a given role. They received a score of '{num}'. \nThe job description was: '{jd}'.\nYou are an expert on interviews. Analyze the above transcript critically, and provide helpful, actionable tips on how the user can improve their suitability for the given role and thus improve their score.\n answer format: \n'What you did right:' followed by a brief bulleted list of things the user did right. In the case that the user did not do anything right, perhaps include just one point, regarding their willingness to engage and improve. \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \neach tip should be 1 sentence long. If the transcript is empty, in the report mention that No information was provided. Do not reply in markdown format, just give me clean text with points"""
        
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.format(text=transcript, num=score, jd=self.job_desc)}],
        )
        
        return response.choices[0].message.content

    def run_evaluation(self, audio_path):
        # job_desc = input("Paste your job description:\n\n")
        # transcript = "I would be a great fit for this role because of my ability to develop creative marketing strategies and adapt to changing trends. In my previous role, I led a campaign that boosted brand engagement by 40% through social media storytelling and community-driven initiatives. With a strong background in event planning and public relations, I’ve built valuable industry connections and enhanced brand visibility. While I may not have extensive experience in certain digital tools, I’m a fast learner, eager to explore new technologies, and passionate about crafting compelling brand messages that drive engagement."
        a = AudioTranscriber()
        transcript=a.transcribe(audio_path)
        score = self.role_fit_score(transcript)        
        print("\n")
        print(f"Role fit score: {score:.2f}%")
        report = self.report_gen(transcript, score)
        print("\n\nREPORT:\n\n", report)

if __name__ == "__main__":
    num = 1 # modify if diff num of q
    ev = RoleFit()
    ev.create_test_q(num)
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    vid = VideoRecorderApp(root, num)
    vid.question_reader(r"role_fit_q.txt")
    root.mainloop()    
    aud_path = r"1_audio\aud_1.wav"
    ev.run_evaluation(aud_path)
