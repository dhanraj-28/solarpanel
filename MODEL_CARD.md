# Model Card: Rooftop Solar Panel Detection System

## Model Overview
This project detects rooftop solar panels from satellite imagery using
computer vision techniques and deep learning (YOLOv8).

The system is designed for automated verification of solar installations
based on geographic coordinates.

---

## Model Details
- **Model Type:** Object Detection
- **Base Architecture:** YOLOv8 (Ultralytics)
- **Frameworks Used:** PyTorch, OpenCV
- **Input:** Satellite images (JPEG)
- **Output:** Detection bounding boxes and solar panel presence

---

## Training Data
- Pretrained YOLOv8n model from Ultralytics
- No custom training performed
- Detection enhanced with OpenCV shape analysis

---

## Inference Pipeline
1. Read latitude and longitude from CSV
2. Download satellite imagery (ESRI World Imagery)
3. Detect solar panels using:
   - Edge detection
   - Contour analysis
   - Aspect ratio filtering
4. Save:
   - Annotated image
   - JSON and CSV outputs

---

## Output Format
Example JSON output:
```json
{
  "serial_no": "1",
  "latitude": 12.9716,
  "longitude": 77.5946,
  "solar_panels_detected": true,
  "num_panels": 3
}
