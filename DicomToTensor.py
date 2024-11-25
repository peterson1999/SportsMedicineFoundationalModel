import os
import pydicom
import torch
import numpy as np
from tqdm import tqdm

def process_dicom_to_tensor(input_dir, output_dir):
    """
    Converts all DICOM files in the input directory to tensors and saves them in the output directory,
    preserving the folder structure.

    Args:
        input_dir (str): Path to the root directory containing DICOM files.
        output_dir (str): Path to the root directory to save tensor files.
    """
    # Collect all folders 
    folder_list = [os.path.join(root) for root, _, _ in os.walk(input_dir)]

    # Progress bar
    for folder in tqdm(folder_list, desc="Processing folders"):
        for file in os.listdir(folder):
            if file.lower().endswith(".dcm"):
                # Input file path
                dicom_path = os.path.join(folder, file)
                
                # Corresponding output path
                relative_path = os.path.relpath(dicom_path, input_dir)
                tensor_output_path = os.path.join(output_dir, os.path.splitext(relative_path)[0] + ".pt")

                # Create output directories
                os.makedirs(os.path.dirname(tensor_output_path), exist_ok=True)
                
                try:
                    
                    dicom_data = pydicom.dcmread(dicom_path)
                    
                    # Extract and normalize the pixel data
                    pixel_array = dicom_data.pixel_array.astype(np.float32)
                    pixel_array = (pixel_array - np.min(pixel_array)) / (np.max(pixel_array) - np.min(pixel_array))
                    
                    # Convert to tensor
                    tensor = torch.from_numpy(pixel_array)

                    # Save tensor to the output path
                    torch.save(tensor, tensor_output_path)
                    print(f"Saved tensor: {tensor_output_path}")
                
                except Exception as e:
                    print(f"Error processing {dicom_path}: {e}")

if __name__ == "__main__":

    input_directory = "/media/rashed/Extreme SSD/Project/Data"  # Input directory
    output_directory = "/media/rashed/Extreme SSD/Project/data(tensor)"  # Output directory

    # Process DICOM files
    process_dicom_to_tensor(input_directory, output_directory)
