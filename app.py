from flask import Flask, render_template, request, redirect, url_for, flash, Response
import cv2
import os
import threading

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # For flash messaging

# Initialize the video capture from the camera
camera = cv2.VideoCapture(0)  # 0 is typically the default camera
camera = None  # Global variable to hold the camera object
camera_lock = threading.Lock() 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Call your model’s prediction function
    prediction = process_video(file_path)
    return render_template('results.html', prediction=prediction, video_file=file.filename)


def generate_frames():
    while True:
        success, frame = camera.read()  # Capture frame-by-frame
        if not success:
            break
        else:
            # Encode the frame in JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Use Flask to yield a byte stream of the frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    global camera
    # Start the camera only if it isn't already started
    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(0)  # Open the camera

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
def live_feed():
    # Render the live feed template
    return render_template('live.html')

if __name__ == "__main__":
    app.run(debug=True)
