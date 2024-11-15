import cv2
import numpy as np
import tensorflow as tf
from moviepy.editor import VideoFileClip
import os
import requests


# Load the pre-trained model
inception_model = tf.keras.models.load_model(r'model\inceptionV3-model.h5')

# Model input image size
image_size = (224, 224)

def send_telegram_message():
    bot_token = '7465229273:AAGAQllb6Z9pu4KjId3WGhsCTE3ywlVjLlM'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': '1398254880',
        'text': 'violence-detected'
    }
    response = requests.post(url, data=data)
    return response.json()

def reencode_video(input_path, output_path):
    # Load the video
    clip = VideoFileClip(input_path)
    
    # Optional: Resize the video if needed for better compatibility
    clip = clip.resize(height=720)  # Example to resize to height 720px, keeping aspect ratio
    
    # Write the video using H.264 codec for video and AAC for audio
    clip.write_videofile(
        output_path, 
        codec='libx264',  # Use libx264 codec (H.264)
        audio_codec='aac',  # Use AAC codec for audio
        threads=4,  # Using multiple threads for faster processing
        preset='ultrafast',  # Optionally, choose a preset (ultrafast is fastest)
        ffmpeg_params=['-movflags', '+faststart']  # Optimize for streaming (fast start)
    )


# Function to preprocess and predict violence for video frames and save output video
def predict_violence(video_path, file_name, model=inception_model, threshold=0.5):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    temp_path = r'uploads\\temp_output.mp4'
    output_path = r'static\\videos\\output.mp4'
    output_name = r'output.mp4'
    
    # Define VideoWriter to save the output video
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_path, fourcc, fps, (frame_width, frame_height))

    frame_predictions = []
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Resize frame to model's expected input size
        frame_resized = cv2.resize(frame, image_size)
        frame_array = tf.keras.preprocessing.image.img_to_array(frame_resized)
        frame_array = np.expand_dims(frame_array, axis=0) / 255.0  # Normalize

        # Predict violence probability
        prediction = model.predict(frame_array)
        prediction_score = prediction[0][0]
        frame_predictions.append(prediction_score)
        
        # Overlay text and bounding box on the frame
        label = "Violence" if prediction_score >= threshold else "Non-Violence"
        color = (0, 0, 255) if label == "Violence" else (0, 255, 0)
        cv2.putText(frame, f"{label}: {prediction_score:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        # Draw a bounding box if violence is detected
        if label == "Violence":
            cv2.rectangle(frame, (10, 10), (frame_width - 10, frame_height - 10), color, 3)

        # Write frame with overlay to output video
        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    # Re-encode video for compatibility
    reencode_video(temp_path, output_path)  # Ensure compatibility with browsers

    # Delete temporary file after re-encoding
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # Determine overall classification based on average prediction
    average_prediction = np.mean(frame_predictions)
    if average_prediction >= threshold:
        print("Overall Prediction: Violence")
        send_telegram_message()
    else:
        print("Overall Prediction: Non-Violence")

    return 'violence' if average_prediction >= threshold else 'Non-Violence', output_path
