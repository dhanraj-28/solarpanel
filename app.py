import sys
import os

# Add src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from pipeline import run_pipeline

if __name__ == "__main__":
    input_csv = "data/input.csv"
    output_folder = "data/outputs"

    run_pipeline(input_csv, output_folder)
