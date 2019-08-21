import json
import pickle
from imutils import face_utils
import cv2
import dlib
import face_recognition
from scipy.spatial import distance as dist

import socketio

sio = socketio.Client()
sio.connect('http://localhost:5000')
sio.emit('join_room', 'room_face')
sio.emit('join_room', 'room_access_denied')
sio.emit('join_room', 'room_fingerprint')
sio.emit('join_room', 'room_blink')

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
data = pickle.loads(open("encodings.pickle", "rb").read())

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 3

class VideoCamera(object):

    COUNTER = 0
    TOTAL = 0

    def __init__(self):
        # Using OpenCV to capture from device 0. If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        self.video = cv2.VideoCapture(0)
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')

    def __del__(self):
        self.video.release()

    def eye_aspect_ratio(self, eye):
        # compute the euclidean distances between the two sets of
        # vertical eye landmarks (x, y)-coordinates
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # compute the euclidean distance between the horizontal
        # eye landmark (x, y)-coordinates
        C = dist.euclidean(eye[0], eye[3])

        # compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

        # return the eye aspect ratio
        return ear

    def get_frame(self):
        success, image = self.video.read()
        # We are using Motion JPEG, but OpenCV defaults to capture raw images,
        # so we must encode it into JPEG in order to correctly display the
        # video stream.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # detect faces in the grayscale frame
        faces = detector(gray, 0)

        for face in faces:
            shape = predictor(gray, face)
            shape = face_utils.shape_to_np(shape)

            (x, y, w, h) = face_utils.rect_to_bb(face)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            leftEye = shape[lStart:lEnd]
            rightEye = shape[rStart:rEnd]

            leftEAR = self.eye_aspect_ratio(leftEye)
            rightEAR = self.eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0

            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(image, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(image, [rightEyeHull], -1, (0, 255, 0), 1)

            if ear < EYE_AR_THRESH:
                VideoCamera.COUNTER += 1

                # otherwise, the eye aspect ratio is not below the blink
                # threshold
            else:
                # if the eyes were closed for a sufficient number of
                # then increment the total number of blinks
                if VideoCamera.COUNTER >= EYE_AR_CONSEC_FRAMES:
                    VideoCamera.TOTAL += 1

                # reset the eye frame counter
                VideoCamera.COUNTER = 0

                # draw the total number of blinks on the frame along with
                # the computed eye aspect ratio for the frame
            cv2.putText(image, "Blinks: {}".format(VideoCamera.TOTAL), (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            if VideoCamera.TOTAL >= 1:
                encodings = face_recognition.face_encodings(rgb)
                names = []

                for encoding in encodings:
                    matches = face_recognition.compare_faces(data["encodings"], encoding)
                    name = 'lalala'
                    if True in matches:
                        matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                        counts = {}
                        for i in matchedIdxs:
                            name = data["names"][i]
                            counts[name] = counts.get(name, 0) + 1
                        name = max(counts, key=counts.get)

                        sio.emit('face_event', json.dumps({'link': 'static/img/logo.png', 'name': name}))
                        print("Welcome {}! Door is unlocked.".format(name))
                        VideoCamera.TOTAL = 0
                    else:
                        sio.emit('access_denied_event', json.dumps({'type': 'face'}))
                        print("no dataset")
                        VideoCamera.TOTAL = 0

                    names.append(name)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()