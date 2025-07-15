import cv2
import numpy as np
import pyttsx3
from simpleFaceRecognition import SimpleFacerec
from collections import defaultdict

sfr = SimpleFacerec()
sfr.load_encoding_images("images/")  

engine = pyttsx3.init()
engine.setProperty('rate', 150)  
engine.setProperty('volume', 0.9)  


announced_names = defaultdict(int)

net = cv2.dnn.readNet("yolov4-tiny.weights", "yolov4-tiny.cfg")
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

# Load COCO class labels
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

spoken_labels = set()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # -------------------- Face Detection --------------------
    face_locations, face_names = sfr.detect_known_faces(frame)
    # Draw rectangles and display names for faces
    for face_loc, name in zip(face_locations, face_names):
        top, right, bottom, left = face_loc
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
        cv2.rectangle(frame, (left, bottom + 10), (right, bottom + 40), (0, 255, 0), cv2.FILLED)
        cv2.putText(
            frame,
            name,
            (left + 10, bottom + 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        if name not in announced_names or announced_names[name] > 20:
            engine.say(f"Hello, {name}")
            engine.runAndWait()
            announced_names[name] = 0
        announced_names[name] += 1

    # -------------------- Object Detection --------------------
    height, width, channels = frame.shape
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    detections = net.forward(output_layers)
    current_frame_labels = set()
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                label = f"{classes[class_id]}: {int(confidence * 100)}%"
                current_frame_labels.add(classes[class_id]) 
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    new_labels = current_frame_labels - spoken_labels
    for label in new_labels:
        engine.say(f"There is a {label}")
        engine.runAndWait()

    spoken_labels.update(new_labels)

    cv2.imshow("Face and Object Detection", frame)
    # Exit on pressing 'Esc' key
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
engine.stop()

