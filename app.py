from flask import Flask, render_template, request, redirect, url_for, flash, Response
import inceptionv3 as inception
import cv2
import numpy as np
import threading

app = Flask(__name__, static_folder="static")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # For flash messaging


# Initialize the video capture from the camera
camera = cv2.VideoCapture(0)  # 0 is typically the default camera
# camera = None  # Global variable to hold the camera object
camera_lock = threading.Lock() 


# Load model and define image size from inception module
model = inception.inception_model
image_size = inception.image_size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

# Preprocessing function for live feed frames
def preprocess_frame(frame):
    frame_resized = cv2.resize(frame, image_size)
    frame_normalized = frame_resized / 255.0
    return np.expand_dims(frame_normalized, axis=0)

# Generator function for video feed
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Preprocess and predict on each frame
            processed_frame = preprocess_frame(frame)
            prediction = model.predict(processed_frame)
            label = "Violence" if prediction[0][0] > 0.5 else "Non-Violence"
            color = (0, 0, 255) if label == "Violence" else (0, 255, 0)

            # Add prediction label to frame
            cv2.putText(frame, f'Prediction: {label}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                        1, color, 2, cv2.LINE_AA)
            
            if label == "Violence":
                inception.send_telegram_message()

            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Use Flask's streaming response
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def gen_frames():
        global camera
        while camera.isOpened():
            success, frame = camera.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


ALLOWED_EXTENSIONS = ['mp4']

#-------------------------ROUTES----------------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        flash('No Video File Found')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        file_path = "static/videos/" + file.filename
        file.save(file_path)

        prediction, output_name = inception.predict_violence(video_path=file_path, file_name=file.filename)
        return render_template('results.html', prediction=prediction, mimetype='video/mp4', video_name = output_name)
    else:
        flash('Invalid File Type')
        return redirect(request.url)


@app.route('/video_feed')
def video_feed():
    global camera
    # Start the camera only if it isn't already started
    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)  # Open the camera
    
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    """Route to stop the camera when the /live route is closed"""
    global camera
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None  # Set camera to None to indicate it's off
    return '', 204  # Return a "No Content" response

@app.route('/live')
def live():
    """Route to render the live feed page."""
    return render_template('live.html')

@app.route('/live_feed')
def live_feed():
    """Route to stream video frames with violence prediction."""
    global camera
    # Start the camera only if it isn't already started
    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0) 
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    app.run(port = 5000, debug=True)
