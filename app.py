import sys
import os

# Add src folder to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from pipeline import run_pipeline

if __name__ == "__main__":
    # Input and output paths
    input_csv = "data/input.csv"
    output_folder = "data/outputs"
    
    # Validate input file exists
    if not os.path.exists(input_csv):
        print(f"Error: Input CSV file not found at '{input_csv}'")
        print("Please create the file or check the path.")
        sys.exit(1)
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Run the pipeline
    try:
        print(f"Starting solar panel detection pipeline...")
        print(f"Input CSV: {input_csv}")
        print(f"Output folder: {output_folder}")
        print("-" * 50)
        
        run_pipeline(input_csv, output_folder)
        
        print("-" * 50)
        print("Pipeline completed successfully!")
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during pipeline execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)