import numpy as np
import cv2
import tensorflow as tf
import random
import mediapipe as mp
from moviepy.editor import VideoFileClip
import os
from telegram import send_telegram_message

# Load the trained model
tcn_model = tf.keras.models.load_model(r'model\\SafeVision_tcn_model.h5')

# Initialize MediaPipe Pose model and drawing utilities
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.3, min_tracking_confidence=0.3)

def pad_and_normalize(image):
    target_size = (224, 224)
    padded_image = np.zeros((target_size[0], target_size[1], 3), dtype=image.dtype)
    h, w, _ = image.shape
    pad_h = (target_size[0] - h) // 2
    pad_w = (target_size[1] - w) // 2
    padded_image[pad_h:pad_h + h, pad_w:pad_w + w, :] = image
    normalized_image = padded_image / 255.0
    return normalized_image

def augment_frame(frame):
    angle = random.uniform(-20, 20)
    height, width = frame.shape[:2]
    center = (width // 2, height // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    frame = cv2.warpAffine(frame, M, (width, height))
    tx = random.uniform(-width * 0.2, width * 0.2)
    ty = random.uniform(-height * 0.2, height * 0.2)
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    frame = cv2.warpAffine(frame, M, (width, height))
    if random.random() > 0.5:
        frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (224, 224))
    return frame

def extract_and_draw_pose(frame):
    # Ensure input is RGB for MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(frame_rgb)
   
    if result.pose_landmarks:
        # Draw pose landmarks on the original frame
        mp_drawing.draw_landmarks(frame, result.pose_landmarks, mp_pose.POSE_CONNECTIONS)
    return frame, result.pose_landmarks

def reencode_video(input_path, output_path):
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, codec="libx264")

def predict_violence(video_path, model = tcn_model , threshold=0.5):
    cap = cv2.VideoCapture(video_path)
    violence_count = 0
    non_violence_count = 0
    frame_number = 0
    
    temp_path = r'uploads\\temp_output.mp4'
    output_path = r'static\\videos\\output.mp4'
    output_name = r'output.mp4'

    # Define the codec and create VideoWriter object
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    out = cv2.VideoWriter(temp_path, cv2.VideoWriter_fourcc(*'XVID'), fps, (frame_width, frame_height))
   
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1

        # Extract and draw pose keypoints on the frame
        frame_with_pose, keypoints = extract_and_draw_pose(frame)
       
        # Preprocess frame for TCN model
        frame_resized = cv2.resize(frame, (224, 224))
        augmented_frame = augment_frame(frame_resized)
        frame_array = pad_and_normalize(augmented_frame)
        frame_array = np.expand_dims(frame_array, axis=0)

        # Predict violence probability
        prediction = model.predict(frame_array)[0][0]

        color = (0, 0, 255)
       
        # Display violence detection result on frame
        if prediction >= threshold:
            label = f"Violence"
            violence_count += 1
            color = (0, 0, 255)
        else:
            label = f"Non-Violence"
            non_violence_count += 1
            color = (0, 255, 0)

        # Overlay the prediction label on the frame
        cv2.putText(frame_with_pose, f"{label} Detected : {prediction:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        # Draw a bounding box if violence is detected
        if label == "Violence":
            cv2.rectangle(frame, (10, 10), (frame_width - 10, frame_height - 10), color, 3)

        # Write the frame with pose and label to the output video
        out.write(frame_with_pose)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Re-encode video for compatibility
    reencode_video(temp_path, output_path)

    # Delete temporary file after re-encoding
    if os.path.exists(temp_path):
        os.remove(temp_path)
   
    print(f"\nTotal violence frames: {violence_count}")
    print(f"Total non-violence frames: {non_violence_count}")

    if violence_count > non_violence_count:
        print("Overall Prediction: Violence")
        send_telegram_message()
    else:
        print("Overall Prediction: Non-Violence")
    
    return 1 if violence_count > non_violence_count else 0, output_name


