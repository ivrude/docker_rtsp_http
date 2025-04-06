from flask import Flask, Response
import cv2
import threading
import queue


app = Flask(__name__)


frame_queue = queue.Queue(maxsize=10)
rtsp_camrera = 'rtsp://admin:p@ssw0rd@192.168.0.44:554'

def capture_frames():
    cap = cv2.VideoCapture(rtsp_camrera)
    if not cap.isOpened():
        print("Error: Unable to open video source")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            continue

        if frame_queue.full():
            for i in range(6):
                frame_queue.get()
                i=i+1

        frame_queue.put(frame)

def generate(scale):
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("Failed to encode frame")
                continue

            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(0.365),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_feed_small')
def video_feed_small():
    return Response(generate(scale=0.2), 
                    mimetype='multipart/x-mixed-replace; boundary=frame'

if __name__ == '__main__':
    capture_thread = threading.Thread(target=capture_frames)
    capture_thread.start()
    app.run(host='0.0.0.0', port=8888)
