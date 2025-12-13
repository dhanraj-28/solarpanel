# Rooftop Solar Verification System

This project implements an **automated solar rooftop verification system** using
free satellite imagery and computer vision techniques.

The goal is to verify whether **solar panels are installed on rooftops** for a given
set of GPS coordinates, reducing the need for manual physical inspections.

---

##  Features

- Accepts latitude & longitude as input (CSV)
- Downloads **free satellite images** (ESRI World Imagery)
- Detects solar panels using **Computer Vision (OpenCV)**
- Marks detected panels on images
- Outputs results in **JSON format**
- Generates a **Model Card** for transparency and auditability
- Fully offline after image download
- No paid API keys required

---

## Project Structure
Solar-Verification/
│
├── data/
│ ├── images/ # Downloaded satellite images
│ ├── outputs/ # Annotated images
│ └── input.csv # Input coordinates
│
├── models/
│ └── yolov8n.pt # Base YOLO model (optional)
│
├── src/
│ ├── download_image.py
│ ├── detect_solar.py
│ ├── pipeline.py
│ ├── quantify.py
│ ├── explain.py
│
├── outputs/
│ ├── results.json
│
├── model_card.md
├── app.py
├── requirements.txt
└── README.md
