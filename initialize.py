import os
import sys

def initialize_paths():
    # Determine current directory of this script
    current_path = os.path.dirname(os.path.abspath(__file__))

    # Change working directory to the script's location
    os.chdir(current_path)

    # Add helper module paths (e.g., tomo_extract and dicom_tools) to the system path
    tomo_extract_path = os.path.join(current_path, "tomo_extract")
    dicom_tools_path = os.path.join(current_path, "dicom_tools")

    # Ensure helper directories exist
    if not os.path.exists(tomo_extract_path):
        raise FileNotFoundError(f"Missing directory: {tomo_extract_path}")
    if not os.path.exists(dicom_tools_path):
        raise FileNotFoundError(f"Missing directory: {dicom_tools_path}")

    # Add directories to system path
    sys.path.append(tomo_extract_path)
    sys.path.append(dicom_tools_path)

    print("Initialization completed. Helper paths are set up successfully.")

# # Call the initialization function
# initialize_paths()
