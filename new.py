import cv2
import customtkinter as ctk 
from PIL import Image
import time
import threading
import pyaudio 
import wave
import os
import random

os.makedirs("2_video", exist_ok=True) 
os.makedirs("1_audio", exist_ok=True)

class VideoRecorderApp:
    def __init__(self, root, num_q=5):
        self.root = root
        self.root.title("Video Recorder")
        self.root.geometry("700x600")
        self.countdown_id = None
        self.questions = [
            "Tell me about yourself.",
            "Tell me about a time when you demonstrated leadership?",
            "Tell me about a time when you were working with a team and faced a challenge. How did you overcome the problem?",
            "What is one of your weaknesses and how do you plan to overcome it?",
            "Tell me about a time you made a mistake at work. How did you resolve the problem, and what did you learn from your mistake?",
            "Give an example of a time when you had to make a difficult decision. How did you handle it?",
            "Tell me about settling into your last job. What did you do to learn the ropes?",
            "Tell me about a time when you had to make a decision without all the information you needed.",
            "Tell me about a time you failed. How did you deal with the situation?",
            "Tell me about a situation when you had a conflict with a teammate."
        ]
        self.selected_questions = self.questions[0:num_q]
        # as of rn no random questions so that calling the questions in other files where needed wont be an issue
        # self.selected_questions = [self.questions[random.randint(0, len(self.questions) - 1)] for _ in range(num_q)]
        self.current_question = 0
        print(self.selected_questions[self.current_question])

        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)

        self.cap = cv2.VideoCapture(0)
        self.recording = False
        self.audio_recording = False
        self.record_count = 1
        self.video_filename = self.get_new_filename("2_video", "vid", "avi")
        self.audio_filename = self.get_new_filename("1_audio", "aud", "wav")
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.fps = 30.0
        self.frame_size = (640, 480)
        self.out = None
        self.warning_label = ctk.CTkLabel(root, text="")
        self.warning_label.pack(pady=5)
        self.count = 10
        self.video_label = ctk.CTkLabel(root, text="")
        self.video_label.pack(pady=10)
        
        self.start_button = ctk.CTkButton(root, text="Start Recording", command=self.start_recording)
        self.start_button.pack(pady=5)
        
        self.go_button = ctk.CTkButton(root, text="Next Question", command=self.next_question, state="disabled")
        self.go_button.pack(pady=5)
        
        self.stop_button = ctk.CTkButton(root, text="Stop Recording", command=self.stop_recording, state="disabled")
        self.stop_button.pack(pady=5)

        self.quit_button = ctk.CTkButton(root, text="Quit", command=self.end_test)
        self.quit_button.pack(pady=5)

        self.uf_id = None
        
        self.update_video()

    def update_video(self):
        """Continuously update the video feed."""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img
        self.uf_id = self.root.after(10,self.update_video)   

    def next_question(self):
        """Displays the next question in the randomly selected list."""
        if self.recording:
            self.new_recording() # to stop the current rec
        self.warning_label.configure(fg_color = "#050c30", text="") 
        self.current_question+=1    
        if self.current_question < len(self.selected_questions): 
            self.new_recording() # to start a new recording
            print(self.selected_questions[self.current_question])
        elif self.go_button.cget("text") == "Submit Test": 
            self.root.after_cancel(self.uf_id)
            self.video_label.configure(image=None, text="Video feed")
            self.video_label.image = None
            self.stop_recording()
            print("Submitting the test...")  
            return
        else:
            self.go_button.configure(text="Submit Test") 
            self.go_button.configure(state="normal")
            self.start_button.configure(state="disabled")

    def start_recording(self):
        """Start recording video and audio."""
        if not self.recording:
            self.video_filename = self.get_new_filename("2_video", "vid", "avi")
            self.audio_filename = self.get_new_filename("1_audio", "aud", "wav")
            self.out = cv2.VideoWriter(self.video_filename, self.fourcc, self.fps, self.frame_size)
            self.recording = True
            self.audio_recording = True
            
            self.video_thread = threading.Thread(target=self.record_video)
            self.audio_thread = threading.Thread(target=self.record_audio)
            
            self.video_thread.start()
            self.audio_thread.start()

            self.timer_val = 5 # modify this to make the countdown appear at a different timing
            self.timer = threading.Timer(self.timer_val, self.countdown)  
            self.timer.start()

            self.start_button.configure(state="disabled")
            self.go_button.configure(state="normal")
            self.stop_button.configure(state="normal")

    def record_video(self):
        """Records video frames in a separate thread."""
        while self.recording:
            ret, frame = self.cap.read()
            if ret:
                self.out.write(frame)
        self.out.release()

    def new_recording(self):
        """Stop current recording and start a new one."""
        if self.recording:
            self.stop_recording()
            if self.countdown_id:
                self.root.after_cancel(self.countdown_id)
                self.count = 10
                self.warning_label.configure(text="")
            self.record_count += 1
            time.sleep(1)
        elif not self.recording:
            self.warning_label.configure(text="")
            self.start_recording()

    def countdown(self):
        if self.count > 0 :
            self.warning_label.configure(fg_color="yellow", text=f"⚠️ Recording will stop in {self.count} seconds!", text_color="black")
            self.count -= 1
            self.countdown_id = self.root.after(1000, self.countdown) 
        else:
            self.recording = False
            self.audio_recording = False
            self.video_thread.join()
            self.audio_thread.join()
            print(f"Saved video: {self.video_filename}")
            print(f"Saved audio: {self.audio_filename}")
            self.stop_button.configure(state="disabled")
            self.warning_label.configure(fg_color = "yellow",text = "Press go to continue >:(")
            self.count = 10
            self.record_count+=1

    def stop_recording(self):
        """Stop recording video and audio."""
        if self.recording:
            self.recording = False
            self.audio_recording = False
            self.timer.cancel()
            
            self.video_thread.join()
            self.audio_thread.join()
            
            print(f"Saved video: {self.video_filename}")
            print(f"Saved audio: {self.audio_filename}")
            
            self.start_button.configure(state="normal")
            self.go_button.configure(state="disabled")
            self.stop_button.configure(state="disabled")

    def record_audio(self):
        """Records audio using pyaudio and saves it to a WAV file."""
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100
        audio = pyaudio.PyAudio()
        stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
        frames = []

        while self.audio_recording:
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(self.audio_filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(audio.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))

    def get_new_filename(self, dir, prefix, extension):
        """Generates a new filename."""

        return f"{dir}/{prefix}_{self.record_count}.{extension}"

    def quit_app(self):
        """Release resources and exit."""
        if self.recording or self.audio_recording:
            self.recording = False
            self.audio_recording = False
            self.timer.cancel()
            self.video_thread.join()
            self.audio_thread.join()
            self.cap.release()
            if self.out:
                self.out.release()
        self.root.destroy()
    
    def end_test(self):
        if self.recording or self.audio_recording:
            self.recording = False
            self.audio_recording = False
            self.timer.cancel()
            self.video_thread.join()
            self.audio_thread.join()
            self.cap.release()
            if self.out:
                self.out.release()
        for folder in ["2_video", "1_audio"]:
            for file in os.listdir(folder):
                os.remove(os.path.join(folder, file))
        self.root.destroy()


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    app = VideoRecorderApp(root)
    root.mainloop()
