import numpy as np
import cv2
import tensorflow as tf
import random

# Load the trained model
tcn_model = tf.keras.models.load_model(r'model\tcn_model.h5')

def pad_and_normalize(image):
    # Pad the image to maintain aspect ratio
    target_size = (224, 224)
    padded_image = np.zeros((target_size[0], target_size[1], 3), dtype=image.dtype)
    
    # Compute padding sizes
    h, w, _ = image.shape
    pad_h = (target_size[0] - h) // 2
    pad_w = (target_size[1] - w) // 2

    # Fill the padded area with the original image
    padded_image[pad_h:pad_h + h, pad_w:pad_w + w, :] = image
    
    # Normalize the image
    normalized_image = padded_image / 255.0
    
    return normalized_image

def augment_frame(frame):
    # Randomly apply augmentations to the frame
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
    
    # Ensure final size is 224x224 after all augmentations
    frame = cv2.resize(frame, (224, 224))
    return frame

def predict_violence(video_path, file_name, model=tcn_model, threshold=0.5):
    cap = cv2.VideoCapture(video_path)
    violence_count = 0
    non_violence_count = 0
    frame_number = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_number += 1
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame, (224, 224))

        # Apply augmentation (optional)
        augmented_frame = augment_frame(frame_resized)
        
        # Preprocess frame
        frame_array = pad_and_normalize(augmented_frame)
        frame_array = np.expand_dims(frame_array, axis=0)

        # Predict violence probability
        prediction = model.predict(frame_array)[0][0]
        
        # Classify based on threshold and count
        if prediction >= threshold:
            print(f"Frame {frame_number}: Violence detected (Score: {prediction:.2f})")
            violence_count += 1
        else:
            print(f"Frame {frame_number}: Non-violence detected (Score: {prediction:.2f})")
            non_violence_count += 1

    cap.release()
    
    print(f"\nTotal violence frames: {violence_count}")
    print(f"Total non-violence frames: {non_violence_count}")

    return 1 if violence_count > non_violence_count else 0


predict_violence("uploads/NV_32.mp4")


