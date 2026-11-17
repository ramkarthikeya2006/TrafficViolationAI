
from ultralytics import YOLO
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "yolov8n.pt"

model = YOLO(str(MODEL_PATH))

VEHICLE_CLASSES = {
    2: "Car",
    3: "Motorcycle",
    5: "Bus",
    7: "Truck"
}

def detect_vehicles(video_path):
    detections = []

    results = model.predict(
        source=str(video_path),
        conf=0.25,
        save=True,
        verbose=False,
        stream=True
    )

    for frame_number, result in enumerate(results, start=1):
        print("Frame:", frame_number)
        print("Boxes found:", len(result.boxes))

        for box in result.boxes:
            class_id = int(box.cls[0])

            if class_id in VEHICLE_CLASSES:
                detections.append({
                    "vehicle": VEHICLE_CLASSES[class_id],
                    "confidence": round(float(box.conf[0]), 2),
                    "frame": frame_number
                })

    print("Total vehicle detections:", len(detections))
    return detections
