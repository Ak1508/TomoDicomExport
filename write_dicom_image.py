import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
import logging

def write_dicom_image(image_data, output_prefix, plan_metadata):
    """
    Write the provided image data to a series of DICOM files.

    Args:
        image_data (dict): Contains the image array and metadata (start, width, and data fields).
        output_prefix (str): Path and prefix for output DICOM files.
        plan_metadata (dict): Contains DICOM header information (e.g., patient name, UID).

    Returns:
        list: SOP Instance UIDs of the written images.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("write_dicom_image")

    # Validate image_data contains required fields
    if not all(key in image_data for key in ["start", "width", "data"]):
        raise ValueError("Image data must contain 'start', 'width', and 'data' fields.")

    # Preprocessing for negative values
    if np.min(image_data["data"]) < 0:
        logger.info("Adjusting negative values in data by adding 1024.")
        image_data["data"] += 1024

    # Create File Meta Information dataset
    file_meta = Dataset()
    file_meta.FileMetaInformationVersion = b'\x00\x01'
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
    file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    file_meta.ImplementationClassUID = '1.2.40.0.13.1.1'

    sop_instance_uids = []

    print ("what is image data :", image_data['data'])

    # Iterate through slices
    for i in range(image_data["data"].shape[2]):
        logger.info(f"Processing slice {i + 1}.")

        # Create the DICOM dataset
        ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\x00" * 128)
        ds.Modality = 'CT'
        ds.ImageType = ['ORIGINAL', 'PRIMARY', 'AXIAL']

        # Add patient and study information
        ds.PatientName = plan_metadata.get("patientName", "UNKNOWN")
        ds.PatientID = plan_metadata.get("patientID", "00000000")
        ds.StudyInstanceUID = plan_metadata.get("studyUID", pydicom.uid.generate_uid())
        ds.SeriesInstanceUID = plan_metadata.get("seriesUID", pydicom.uid.generate_uid())
        ds.FrameOfReferenceUID = plan_metadata.get("frameRefUID", pydicom.uid.generate_uid())

        # Set image-specific metadata
        ds.SOPInstanceUID = pydicom.uid.generate_uid()
        sop_instance_uids.append(ds.SOPInstanceUID)
        ds.InstanceNumber = i + 1
        ds.SliceThickness = image_data["width"][2] * 10
        ds.PixelSpacing = [image_data["width"][0] * 10, image_data["width"][1] * 10]
        ds.Rows, ds.Columns = image_data["data"].shape[:2]
        ds.ImagePositionPatient = [
            image_data["start"][0] * 10,
            image_data["start"][1] * 10,
            (image_data["start"][2] + i * image_data["width"][2]) * 10,
        ]
        ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
        ds.SamplesPerPixel = 1
        ds.PhotometricInterpretation = "MONOCHROME2"
        ds.BitsAllocated = 16
        ds.BitsStored = 16
        ds.HighBit = 15
        ds.PixelRepresentation = 0
        ds.RescaleIntercept = -1024
        ds.RescaleSlope = 1

        # Debugging metadata values
        logger.debug(f"Slice {i + 1} metadata: {ds}")

        # Apply transformations to pixel data
        pixel_data = np.flip(np.rot90(image_data["data"][:, :, i], 3), 1)
        ds.PixelData = pixel_data.astype(np.uint16).tobytes()

        # Set file creation date and time
        dt = datetime.now()
        ds.InstanceCreationDate = dt.strftime("%Y%m%d")
        ds.InstanceCreationTime = dt.strftime("%H%M%S")

        # Write the DICOM file
        output_file = f"{output_prefix}_{i + 1:03d}.dcm"
        pydicom.dcmwrite(output_file, ds)
        logger.info(f"Written slice {i + 1} to {output_file}.")

    return sop_instance_uids
