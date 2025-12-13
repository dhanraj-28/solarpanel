import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

# Load YOLO model (fine-tuned for rooftop solar if available)
model = YOLO("models/yolov8n.pt")  # Replace with rooftop PV trained model if available

def enhance_image_contrast(img):
    """Enhance image contrast to make solar panels more visible."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    return gray

def detect_solar_panels_cv(image_path):
    """CV-based backup detection for small rooftop panels."""
    img = cv2.imread(image_path)
    if img is None:
        return False, 0, []

    gray = enhance_image_contrast(img)
    edges = cv2.Canny(gray, 30, 120)  # lower thresholds to catch small panels
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    solar_panels = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 50:  # smaller panels
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                if 0.5 < aspect_ratio < 2.0:
                    roi = gray[y:y+h, x:x+w]
                    if roi.size > 0 and np.mean(roi) < 120:
                        solar_panels.append((x, y, w, h))

    detected = len(solar_panels) > 0
    return detected, len(solar_panels), solar_panels

def detect_solar(input_image, output_path):
    """Detect rooftop solar panels using YOLO + optional CV backup."""
    try:
        # YOLO detection
        results = model.predict(
            source=input_image,
            imgsz=1024,     # higher resolution
            conf=0.1,       # lower confidence for small objects
            iou=0.2,
            augment=True,   # test-time augmentation
            save=False
        )

        yolo_boxes = []
        for r in results:
            if r.boxes is not None:
                for box in r.boxes.xyxy:
                    x1, y1, x2, y2 = box.tolist()
                    yolo_boxes.append((int(x1), int(y1), int(x2-x1), int(y2-y1)))

        # Optional CV backup detection
        detected_cv, count_cv, cv_boxes = detect_solar_panels_cv(input_image)

        # Merge YOLO + CV detections
        final_boxes = yolo_boxes + cv_boxes
        detected = len(final_boxes) > 0

        # Annotate image
        img = Image.open(input_image)
        draw = ImageDraw.Draw(img)
        for (x, y, w, h) in final_boxes:
            draw.rectangle([x, y, x+w, y+h], outline="green", width=3)

        # Text overlay
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        text = f"SOLAR PANELS DETECTED: {len(final_boxes)}" if detected else "NO SOLAR PANELS DETECTED"
        color = (0, 255, 0) if detected else (255, 0, 0)
        draw.rectangle([(10, 10), (600, 70)], fill=(0, 0, 0))
        draw.text((20, 20), text, fill=color, font=font)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"Detection saved: {output_path}")

        # Mock result to match previous interface
        class MockResult:
            def __init__(self, count):
                self.boxes = [1] * count

        return MockResult(len(final_boxes))

    except Exception as e:
        print(f"Error in detection: {e}")
        import traceback
        traceback.print_exc()
        raise
