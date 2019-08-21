import json
import time
from flask import Flask, render_template, Response, request
from camera import VideoCamera
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


# global variable
global_face = None
global_access = None
global_finger = None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/api/post/face', methods=['POST'])
def api_post_face():
    if request.method == 'POST':
        data = request.json
        link = data['link']
        name = data['name']
        response = {'name': name, 'link': link}
        global global_face
        global_face = json.dumps(response)
        return global_face


@app.route('/api/post/access-denied', methods=['POST'])
def api_post_access():
    if request.method == 'POST':
        data = request.json
        type = data['type']
        response = {'type': type}
        global global_access
        global_access = json.dumps(response)
        return global_access


@app.route('/api/post/fingerprint', methods=['POST'])
def api_post_fingerprint():
    if request.method == 'POST':
        data = request.json
        link = data['link']
        name = data['name']
        response = {'name': name, 'link': link}
        global global_finger
        global_finger = json.dumps(response)
        return global_finger


@app.route('/face')
def face():
    return render_template('face.html')


@app.route('/fingerprint')
def fingerprint():
    return render_template('fingerprint.html')


@app.route('/face-success')
def success_face():
    data_face = json.loads(global_face)
    return render_template('face_success.html', face=data_face)


@app.route('/fingerprint-success')
def success_fingerprint():
    fingerprint= json.loads(global_finger)
    return render_template('fingerprint_success.html', fingerprint=fingerprint)


@app.route('/access_denied')
def access_denied():
    change = json.loads(global_access)
    print(change)
    return render_template('access_denied.html', change=change)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5555)