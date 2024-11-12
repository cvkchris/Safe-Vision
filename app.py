from flask import Flask, render_template, request, redirect, url_for, flash, Response
import cv2
import os
import threading
# from tcn import predict_violence
import inceptionv3 as inception

app = Flask(__name__, static_folder="static")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'  # For flash messaging

application = app

# Initialize the video capture from the camera
camera = cv2.VideoCapture(0)  # 0 is typically the default camera
camera = None  # Global variable to hold the camera object
camera_lock = threading.Lock() 



ALLOWED_EXTENSIONS = ['mp4']
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower()

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
def live_feed():
    return render_template('live.html')

if __name__ == "__main__":
    application.run(port = 5000, debug=True)
