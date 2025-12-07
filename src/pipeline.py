import csv
import os

from src.fetch_images import fetch_satellite_image
from src.detect_solar import detect_solar
from src.quantify import compute_area
from src.explain import explain

INPUT_FILE = "data/input.csv"
IMAGE_DIR = "data/images"
OUTPUT_DIR = "data/outputs"

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_pipeline():
    with open(INPUT_FILE, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            id = row["id"]
            lat = float(row["lat"])
            lon = float(row["lon"])

            print("\nProcessing ID:", id)

            image_path = f"{IMAGE_DIR}/{id}.png"
            output_image_path = f"{OUTPUT_DIR}/{id}_detected.png"

            # Step 1: Download satellite image
            success = fetch_satellite_image(lat, lon, image_path)
            if not success:
                print("Skipping ID", id)
                continue

            # Step 2: Detect solar panels
            detection = detect_solar(image_path, output_image_path)

            # Step 3: Compute area
            area = compute_area(detection)

            # Step 4: Generate explanation
            message = explain(area, lat, lon)

            print(message)

            # Save text output
            with open(f"{OUTPUT_DIR}/{id}.txt", "w") as txt:
                txt.write(message)

if __name__ == "__main__":
    run_pipeline()
