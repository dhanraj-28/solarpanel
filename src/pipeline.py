import os
# import sys
import csv
import json

def ensure_directory(path):
    """Ensure a directory exists, removing any file conflicts."""
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
            print(f"Removed file blocking directory: {path}")
    os.makedirs(path, exist_ok=True)

IMAGE_DIR = "data/images"
OUTPUT_DIR = "data/outputs"

ensure_directory(IMAGE_DIR)
ensure_directory(OUTPUT_DIR)

def run_pipeline(input_csv, output_folder):
    """Run the solar panel detection pipeline."""
    
    import importlib.util
    
    src_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Load modules
    download_spec = importlib.util.spec_from_file_location(
        "download_image", 
        os.path.join(src_dir, "download_image.py")
    )
    download_module = importlib.util.module_from_spec(download_spec)
    download_spec.loader.exec_module(download_module)
    
    detect_spec = importlib.util.spec_from_file_location(
        "detect_solar", 
        os.path.join(src_dir, "detect_solar.py")
    )
    detect_module = importlib.util.module_from_spec(detect_spec)
    detect_spec.loader.exec_module(detect_module)
    
    ensure_directory(output_folder)
    
    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")
    
    print(f"Reading CSV: {input_csv}")
    
    results = []
    
    with open(input_csv, 'r') as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, 1):
            try:
                serial_no = row['serial_no']
                latitude = float(row['latitude'])
                longitude = float(row['longitude'])
                
                print(f"\n[{idx}] Processing Serial No: {serial_no}")
                print(f"  Location: ({latitude}, {longitude})")
                
                # Download satellite image for this location
                local_image = os.path.join(IMAGE_DIR, f"location_{serial_no}.jpg")
                print(f"  → Fetching satellite image...")
                download_module.download_satellite_image(latitude, longitude, local_image)
                
                # Detect solar panels
                output_path = os.path.join(output_folder, f"detected_{serial_no}.jpg")
                print(f"  → Running solar panel detection...")
                result = detect_module.detect_solar(local_image, output_path)
                
                # Check if solar panels were detected
                num_detections = len(result.boxes) if hasattr(result, 'boxes') else 0
                solar_present = num_detections > 0
                
                results.append({
                    'serial_no': serial_no,
                    'latitude': latitude,
                    'longitude': longitude,
                    'solar_panels_detected': solar_present,
                    'num_panels': num_detections
                })
                
                status = "✓ SOLAR PANELS FOUND" if solar_present else "✗ NO SOLAR PANELS"
                print(f"  {status} (Count: {num_detections})")
                
            except KeyError as e:
                print(f"  ✗ Error: Missing column {e} in CSV")
            except Exception as e:
                print(f"  ✗ Error processing serial no {row.get('serial_no', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()
    
     # ============================
    # SAVE RESULTS TO CSV
    # ============================
    results_csv = os.path.join(output_folder, "detection_results.csv")
    with open(results_csv, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

    print(f"\n✓ CSV output saved to: {results_csv}")

    # ============================
    # SAVE RESULTS TO JSON (REQUIRED)
    # ============================
    results_json = os.path.join(output_folder, "detection_results.json")
    with open(results_json, "w") as jf:
        json.dump(results, jf, indent=4)

    print(f"✓ JSON output saved to: {results_json}")
    print("\nPipeline finished!")
