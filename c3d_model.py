import numpy as np
import cv2
from tensorflow.keras.models import load_model
from matplotlib import pyplot as plt

model = load_model(r'model\\C3D_model_.h5')

def predict_violence(frames, threshold=0.5):
    frames = np.expand_dims(frames, axis=0)  # Add batch dimension
    prediction = model.predict(frames)
    prob = prediction[0][0]  # Assuming violence probability is in prediction[0][0]
    return "Violence" if prob > threshold else "Non-Violence", prob

def process_video(video_path, frame_size=(112, 112), buffer_size=16, threshold=0.5):
    cap = cv2.VideoCapture(video_path)
    buffer = []

    # Initialize counters
    violence_count = 0
    non_violence_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize and buffer the frame
        frame_resized = cv2.resize(frame, frame_size)
        buffer.append(frame_resized)

        # Make prediction if buffer is full
        if len(buffer) == buffer_size:
            label, prob = predict_violence(np.array(buffer), threshold=threshold)

            # Update counters based on prediction
            if label == "Violence":
                violence_count += 1
            else:
                non_violence_count += 1

            # Display the prediction on the frame
            cv2.putText(frame, f'Prediction: {label} (Prob: {prob:.2f})', (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Reset the buffer by removing the oldest frame
            buffer.pop(0)

        # Display frame with delay based on the video's FPS
        cv2.waitKey(33)  # 30 FPS delay approximation, adjust if necessary

    # Release resources
    cap.release()

    return 1 if violence_count > non_violence_count else 0
