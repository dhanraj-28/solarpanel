def compute_area(detections):
    area = 0

    for box in detections.boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        width = x2 - x1
        height = y2 - y1
        area += width * height

    return area
