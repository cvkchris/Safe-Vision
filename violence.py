import numpy as np
import cv2
from tensorflow.keras.models import load_model

class ViolenceDetector:
    def __init__(self, model_path, max_frames=30):
        self.model = load_model(model_path)
        self.max_frames = max_frames

    def load_video(self, video_path):
        cap = cv2.VideoCapture(video_path)
        frames = []
        while cap.isOpened() and len(frames) < self.max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (64, 64))
            frames.append(frame)
        cap.release()

        if len(frames) < self.max_frames:
            frames += [np.zeros((64, 64, 3), dtype=np.uint8)] * (self.max_frames - len(frames))
        
        return np.array(frames)

    def predict_violence(self, video_path):
        video = self.load_video(video_path)
        prediction = self.model.predict(np.expand_dims(video, axis=0))
        return float(prediction[0][0])

# Initialize the detector
detector = ViolenceDetector('3d_cnn_model.h5')
