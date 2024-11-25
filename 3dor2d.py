import os
import pydicom
from tqdm import tqdm


base_directory = "/media/rashed/Extreme SSD/Project/Data" #change this to your dicome directory

# Collect all DICOM files (handles multiple file structure)
dicom_files = []
for root, _, files in os.walk(base_directory):
    for file in files:
        if file.lower().endswith(".dcm"):
            dicom_files.append(os.path.join(root, file))

print(f"Processing {len(dicom_files)} DICOM files...")

# Function to check if a DICOM file is 2D
def is_2d_slice(dicom_file):
    try:
        # Read the DICOM file
        dicom_data = pydicom.dcmread(dicom_file)

        # Check pixel data dimensions
        rows = dicom_data.get("Rows", None)
        columns = dicom_data.get("Columns", None)

        if rows is None or columns is None:
            return False  # Missing dimensions means it's not a valid 2D slice

        # Check if the pixel data represents a single 2D image
        pixel_data_shape = dicom_data.pixel_array.shape
        if len(pixel_data_shape) == 2:  # Only two dimensions: Rows x Columns
            return True
        else:
            return False  # More than 2 dimensions indicates non-2D data
    except Exception as e:
        print(f"Error processing file {dicom_file}: {e}")
        return False

# Validate all DICOM files
all_2d = True
non_2d_files = []

for dicom_file in tqdm(dicom_files, desc="Checking DICOM files"):
    if not is_2d_slice(dicom_file):
        all_2d = False
        non_2d_files.append(dicom_file)

# Print results
if all_2d:
    print("\nAll files in the dataset are 2D slices.")
else:
    print(f"\nNot all files are 2D slices. {len(non_2d_files)} files are not 2D:")
    for file in non_2d_files:
        print(f" - {file}")
