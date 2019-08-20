import argparse
import pickle
from imutils import face_utils
import cv2
import dlib
import face_recognition

detector = dlib.get_frontal_face_detector()
data = pickle.loads(open("encodings.pickle", "rb").read())



class VideoCamera(object):
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
            (x, y, w, h) = face_utils.rect_to_bb(face)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            encodings = face_recognition.face_encodings(rgb)
            names = []

            for encoding in encodings:
                matches = face_recognition.compare_faces(data["encodings"], encoding)

                if True in matches:
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    name = max(counts, key=counts.get)
                    print("Welcome {}! Door is unlocked.".format(name))
                else:
                    print("no dataset")

                names.append(name)

        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()