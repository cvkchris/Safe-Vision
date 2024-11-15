from flask import Flask, request, jsonify, Response
import inceptionv3 as inception
import cv2
import numpy as np
import threading
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # For secure sessions and flash messaging

# Initialize the video capture from the camera
camera = cv2.VideoCapture(0)  # 0 is typically the default camera
camera_lock = threading.Lock()

# Load model and define image size from inception module
model = inception.inception_model
image_size = inception.image_size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['mp4', 'avi', 'mov', 'mkv']

# Preprocess a frame for prediction
def preprocess_frame(frame):
    frame_resized = cv2.resize(frame, image_size)
    frame_normalized = frame_resized / 255.0
    return np.expand_dims(frame_normalized, axis=0)

# Generator function for streaming video feed
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Preprocess and predict
            processed_frame = preprocess_frame(frame)
            prediction = model.predict(processed_frame)
            label = "Violence" if prediction[0][0] > 0.5 else "Non-Violence"
            color = (0, 0, 255) if label == "Violence" else (0, 255, 0)

            # Add label to the frame
            cv2.putText(frame, f'Prediction: {label}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, color, 2, cv2.LINE_AA)
            
            if label == "Violence":
                inception.send_telegram_message()

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Stream frame to client
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_frames(video_path):
    video_capture = cv2.VideoCapture(video_path)
    while video_capture.isOpened():
        success, frame = video_capture.read()
        if not success:
            break

        # Encode frame in JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            break

        # Convert frame to bytes
        frame_bytes = buffer.tobytes()

        # Yield frame with multipart headers
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    video_capture.release()

# API Endpoints

@app.route('/api/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Prediction on uploaded video
        prediction, output_path = inception.predict_violence(video_path=file_path, file_name=file.filename)

        return jsonify({'prediction': prediction, 'video_stream_url': '/api/video_static'}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/video_feed')
def video_feed():
    """API endpoint to stream live video frames with predictions"""
    global camera
    with camera_lock:
        if not camera.isOpened():
            camera.open(0)  # Reinitialize the camera if not already started
    
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/video_static', methods=['GET'])
def video_feed_static():
    video_path = r'uploads\output.mp4'  # Update this path to your video file
    return Response(gen_frames(video_path),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    """Endpoint to stop the camera when streaming is no longer needed"""
    global camera
    with camera_lock:
        if camera.isOpened():
            camera.release()
    return jsonify({'message': 'Camera stopped'}), 204

@app.route('/api/live_prediction')
def live_prediction():
    """Endpoint to check if camera-based prediction is running."""
    return jsonify({'status': 'Running' if camera.isOpened() else 'Stopped'}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
