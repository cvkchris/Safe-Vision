import cv2
import numpy as np
import tensorflow as tf


# Load the pre-trained model
inception_model = tf.keras.models.load_model(r'model\inceptionV3-model.h5')

# Model input image size
image_size = (224, 224)

# Function to preprocess and predict violence for video frames and save output video
def predict_violence(video_path, file_name, model=inception_model, threshold=0.5):
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    output_path = r'static\\videos\\output.mp4'
    output_name = r'output.mp4'
    
    # Define VideoWriter to save the output video
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

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

    # Determine overall classification based on average prediction
    average_prediction = np.mean(frame_predictions)
    if average_prediction >= threshold:
        print("Overall Prediction: Violence")
    else:
        print("Overall Prediction: Non-Violence")

    return 1 if average_prediction >=threshold else 0, output_name

