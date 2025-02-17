import cv2
import dlib 
import numpy as np
from g4f.client import Client

class KalmanFilter:
    def __init__(self, process_noise=1e-5, measurement_noise=1e-1):
        self.kf = cv2.KalmanFilter(2, 1)  
        self.kf.transitionMatrix = np.array([[1, 1], [0, 1]], dtype=np.float32)
        self.kf.measurementMatrix = np.array([[1, 0]], dtype=np.float32)
        self.kf.processNoiseCov = np.eye(2, dtype=np.float32) * process_noise
        self.kf.measurementNoiseCov = np.eye(1, dtype=np.float32) * measurement_noise
        self.kf.statePost = np.array([[0], [0]], dtype=np.float32)  

    def update(self, measurement):
        self.kf.predict()
        self.kf.correct(np.array([[measurement]], dtype=np.float32))
        return self.kf.statePost[0, 0]  

class EyebrowFurrowDetector:
    def __init__(self, predictor_path = "gaze_tracking/trained_models/shape_predictor_68_face_landmarks.dat"):
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(predictor_path)

        self.kalman_filter = KalmanFilter()
        self.stress_frame_count = 0
        self.stress_labels = []

        self.FURROW_THRESHOLD = 0.16  
        self.STRESS_FRAMES_THRESHOLD = 10  

        self.LEFT_EYEBROW = (17, 18, 19, 20, 21)
        self.RIGHT_EYEBROW = (22, 23, 24, 25, 26)
        self.LEFT_EYE = (36, 37, 38, 39, 40, 41)
        self.RIGHT_EYE = (42, 43, 44, 45, 46, 47)

    def normalized_distance(self, landmarks, eyebrow_indices, eye_indices):
        eyebrow_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in eyebrow_indices])
        eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in eye_indices])
        
        avg_eyebrow_y = np.mean(eyebrow_points[:, 1])
        avg_eye_y = np.mean(eye_points[:, 1])
        vertical_distance = avg_eye_y - avg_eyebrow_y
        
        face_width = abs(landmarks.part(16).x - landmarks.part(0).x)
        
        return vertical_distance / face_width

    def detect_furrow(self, landmarks):
        left_dist = self.normalized_distance(landmarks, self.LEFT_EYEBROW, self.LEFT_EYE)
        right_dist = self.normalized_distance(landmarks, self.RIGHT_EYEBROW, self.RIGHT_EYE)
        avg_dist = (left_dist + right_dist) / 2
        smoothed_dist = self.kalman_filter.update(avg_dist)
        return smoothed_dist < self.FURROW_THRESHOLD

    def process_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        self.stress_labels = []

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)

            for face in faces:
                landmarks = self.predictor(gray, face)
                is_furrowed = self.detect_furrow(landmarks)

                if is_furrowed:
                    self.stress_frame_count += 1
                else:
                    self.stress_frame_count = max(self.stress_frame_count - 1, 0)

                stress_label = 1 if self.stress_frame_count > self.STRESS_FRAMES_THRESHOLD else 0
                self.stress_labels.append(stress_label)

        cap.release()
        return np.array(self.stress_labels)

    def compute_relax_score(self, window_size, step_size, threshold):
        labels = self.stress_labels
        total_frames = len(labels)
        sustained_stress_windows = 0
        total_windows = 0

        for start in range(0, total_frames - window_size + 1, step_size):
            window = labels[start:start + window_size]  
            stress_ratio = sum(window) / window_size  

            if stress_ratio >= threshold:
                sustained_stress_windows += 1  

            total_windows += 1

        return round(100 - ((sustained_stress_windows / total_windows) * 100), 2) if total_windows > 0 else 0  
    
    def report_generate(self, score):
        prompt = "This is how the score is calculated for eyebrow furrowing: The sliding window method divides the sequence into overlapping segments of a fixed size. For each window, the average eyebrow distance is calculated, and the ratio of furrowed frames to total frames in the window is computed. If this ratio exceeds a set threshold, the window is considered stressed. The final score is then determined by subtracting the percentage of stressed windows from 100, representing the overall relaxation level.\nThe score obtained by the user is {score}.\nYou are an expert on body language. Given the method for calculating the score, and the score obtained by the user, provide helpful, actionable tips to the user to improve their relaxation level and thus their score. Provide only what tips are necessary, most importantly KEEP THEM UNIQUE. Do not overwhelm the user with excessive points, and provide information that they can act on even in the short term.\n answer format: \n'What you did right:' followed by a brief bulleted list of things the user did right, and \n'Tips for improvement:' followed by a brief bulleted list of tips, outlining concisely (in simple statements without using unnecessarily complicated language) in each tip what the user can improve, why it's relevant from an interview standpoint, and how the user can improve it. \neach tip should be 1 sentence long. Do not reply in markdown format, just give me clean text with points"
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt.format(score = score)}],
        )        
        # Capture the response text and split into keywords
        #print(prompt)
        result = response.choices[0].message.content
        return result

# Usage Example:
if __name__=="__main__":
    detector = EyebrowFurrowDetector()
    video_path = r"..\2_video\vid_1.avi" # REPLACE WITH VID PATH (i just recorded from mock int and used it)
    stress_array = detector.process_video(video_path)
    stress_score = detector.compute_relax_score(30,15,0.35)
    report = detector.report_generate(stress_score)
    print(f"REPORT\n {report}")
    print(f"Final Stress Score: {stress_score}%")
    # print(stress_array)
