import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO

# Load YOLO model (replace with rooftop PV fine-tuned model if available)
model = YOLO("models/yolov8n.pt")

def enhance_image_clahe(img):
    """Apply CLAHE to enhance local contrast for solar panel detection."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    return clahe.apply(gray)

def detect_solar_panels_cv(image_path):
    """Detect small/angled rooftop panels using CV techniques."""
    img = cv2.imread(image_path)
    if img is None:
        return [], []

    gray = enhance_image_clahe(img)
    edges = cv2.Canny(gray, 30, 100)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    boxes = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 30:  # detect smaller panels
            continue
        rect = cv2.minAreaRect(cnt)  # rotated rectangle
        (x, y), (w, h), angle = rect
        if w == 0 or h == 0:
            continue
        aspect_ratio = max(w, h) / min(w, h)
        if 0.5 < aspect_ratio < 3.0:
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            roi_mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(roi_mask, [box], -1, 255, -1)
            mean_val = cv2.mean(gray, mask=roi_mask)[0]
            if mean_val < 140:  # allow slightly brighter panels
                x_min = np.min(box[:,0])
                y_min = np.min(box[:,1])
                x_max = np.max(box[:,0])
                y_max = np.max(box[:,1])
                boxes.append((x_min, y_min, x_max - x_min, y_max - y_min))

    return boxes

def iou(box1, box2):
    """Compute Intersection over Union for two boxes."""
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    xi1 = max(x1, x2)
    yi1 = max(y1, y2)
    xi2 = min(x1 + w1, x2 + w2)
    yi2 = min(y1 + h1, y2 + h2)
    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    box1_area = w1 * h1
    box2_area = w2 * h2
    union_area = box1_area + box2_area - inter_area

    return inter_area / union_area if union_area > 0 else 0

def merge_detections(yolo_boxes, cv_boxes, iou_threshold=0.3):
    """Merge YOLO and CV detections avoiding duplicates."""
    final_boxes = yolo_boxes.copy()
    for cvb in cv_boxes:
        if all(iou(cvb, yb) < iou_threshold for yb in yolo_boxes):
            final_boxes.append(cvb)
    return final_boxes

def detect_solar(input_image, output_path, tile_size=1024, stride=512):
    """Detect rooftop solar panels using YOLO + CV with tiling."""
    img_full = cv2.imread(input_image)
    if img_full is None:
        raise FileNotFoundError(f"Image not found: {input_image}")

    height, width = img_full.shape[:2]
    yolo_boxes = []

    # Sliding window tiling
    for y in range(0, height, stride):
        for x in range(0, width, stride):
            tile = img_full[y:y+tile_size, x:x+tile_size]
            if tile.shape[0] < 32 or tile.shape[1] < 32:
                continue
            results = model.predict(
                source=tile,
                imgsz=1024,
                conf=0.1,
                iou=0.2,
                augment=True,
                save=False
            )
            for r in results:
                if r.boxes is not None:
                    for box in r.boxes.xyxy:
                        x1, y1, x2, y2 = box.tolist()
                        yolo_boxes.append((
                            int(x1 + x),
                            int(y1 + y),
                            int(x2 - x1),
                            int(y2 - y1)
                        ))

    # CV backup detection
    cv_boxes = detect_solar_panels_cv(input_image)

    # Merge
    final_boxes = merge_detections(yolo_boxes, cv_boxes)

    # Annotate
    img_pil = Image.open(input_image)
    draw = ImageDraw.Draw(img_pil)
    for (x, y, w, h) in final_boxes:
        draw.rectangle([x, y, x+w, y+h], outline="green", width=3)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    text = f"SOLAR PANELS DETECTED: {len(final_boxes)}" if final_boxes else "NO SOLAR PANELS DETECTED"
    color = (0, 255, 0) if final_boxes else (255, 0, 0)
    draw.rectangle([(10, 10), (600, 70)], fill=(0,0,0))
    draw.text((20, 20), text, fill=color, font=font)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img_pil.save(output_path)
    print(f"Detection saved: {output_path}")

    class MockResult:
        def __init__(self, count):
            self.boxes = [1] * count

    return MockResult(len(final_boxes))
