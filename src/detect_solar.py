from ultralytics import YOLO
from PIL import Image

model = YOLO("models/yolov8n.pt")



def detect_solar(input_image, output_path):
    results = model.predict(input_image, save=True, project="data/outputs", name="det")

    # Save a copy into your chosen output path
    result_img = Image.open(results[0].save_dir + "/image0.jpg")
    result_img.save(output_path)

    print("Detection saved:", output_path)
    return results[0]
