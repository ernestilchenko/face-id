import logging

import cv2
import dlib
import face_recognition
import numpy
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import Person

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger()

unknown_face_count = 0
last_save_time = 0
save_interval = 10
known_face_encodings = []
known_face_names = []


def gen():
    cap = cv2.VideoCapture(0)
    predictor_path = "shape/shape_predictor_68_face_landmarks.dat"
    dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(predictor_path)

    # Load known faces and names from database
    persons = Person.objects.all()
    for person in persons:
        image = face_recognition.load_image_file(person.photo.path)
        face_encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(person.name)

    while True:
        ret, frame = cap.read()
        if not ret:
            logger.error("Failed to capture frame from webcam")
            break

        # Ensure the frame is in RGB format
        try:
            rgb_frame = numpy.ascontiguousarray(frame[:, :, ::-1])
        except Exception as e:
            logger.error(f"Error converting frame to RGB: {e}")
            continue

        # Detect faces
        try:
            face_locations = face_recognition.face_locations(rgb_frame)
        except Exception as e:
            logger.error(f"Error in face recognition: {e}")
            continue

        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown Person"

            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
            else:
                pass

            rect = dlib.rectangle(left, top, right, bottom)
            shape = shape_predictor(rgb_frame, rect)

            for i in range(shape.num_parts):
                p = shape.part(i)
                cv2.circle(frame, (p.x, p.y), 1, (0, 255, 0), -1)

            font_scale = 1.0
            font_thickness = 2
            text_size = cv2.getTextSize(name, cv2.FONT_HERSHEY_DUPLEX, font_scale, font_thickness)[0]
            text_x = left + 6
            text_y = top - 10 - text_size[1]

            cv2.putText(frame, name, (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX, font_scale, (0, 255, 0), font_thickness)

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    cap.release()


@login_required
def video_feed(request):
    return StreamingHttpResponse(gen(), content_type='multipart/x-mixed-replace; boundary=frame')


@login_required
def video_view(request):
    return render(request, 'admin/webcam/video.html')


@login_required
@csrf_exempt
def open_door(request):
    if request.method == "POST":
        # Implement your logic to open the door here
        return JsonResponse({"message": "Door opened!"})


@login_required
@csrf_exempt
def close_door(request):
    if request.method == "POST":
        # Implement your logic to close the door here
        return JsonResponse({"message": "Door closed!"})
