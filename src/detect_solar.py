import torch
from torch.serialization import add_safe_globals
from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import os
import numpy as np
import cv2

add_safe_globals([DetectionModel])

model = YOLO("models/yolov8n.pt")


def detect_solar_panels_cv(image_path):
    """
    Detect solar panels using computer vision techniques.
    Looks for rectangular dark patterns typical of solar installations.
    """
    # Read image
    img = cv2.imread(image_path)
    if img is None:
        return False, 0, []
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply edge detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    solar_panels = []
    
    # Look for rectangular shapes (solar panels are rectangular)
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Filter by size (solar panels have minimum size)
        if area > 500:  # Adjust this threshold
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
            
            # Check if shape is rectangular (4 corners)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = float(w) / h
                
                # Solar panels typically have aspect ratio between 0.5 and 2
                if 0.5 < aspect_ratio < 2.0:
                    # Check if region is darker than average (solar panels are dark)
                    roi = gray[y:y+h, x:x+w]
                    if roi.size > 0:
                        avg_brightness = np.mean(roi)
                        if avg_brightness < 100:  # Dark region
                            solar_panels.append((x, y, w, h))
    
    detected = len(solar_panels) > 0
    return detected, len(solar_panels), solar_panels


def detect_solar(input_image, output_path):
    """
    Detect solar panels using CV2 pattern matching.
    """
    try:
        # Use computer vision detection
        detected, count, panels = detect_solar_panels_cv(input_image)
        
        # Open and draw on image
        img = Image.open(input_image)
        draw = ImageDraw.Draw(img)
        
        # Draw detected panels
        for (x, y, w, h) in panels:
            draw.rectangle([x, y, x+w, y+h], outline="green", width=3)
        
        # Add text overlay
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        if detected:
            text = f"SOLAR PANELS DETECTED: {count}"
            color = (0, 255, 0)
        else:
            text = "NO SOLAR PANELS DETECTED"
            color = (255, 0, 0)
        
        # Add semi-transparent background for text
        draw.rectangle([(10, 10), (600, 70)], fill=(0, 0, 0))
        draw.text((20, 20), text, fill=color, font=font)
        
        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        
        print(f"Detection saved: {output_path}")
        
        # Return mock result
        class MockResult:
            def __init__(self, count):
                self.boxes = [1] * count
        
        return MockResult(count)
        
    except Exception as e:
        print(f"Error in detection: {e}")
        import traceback
        traceback.print_exc()
        raise