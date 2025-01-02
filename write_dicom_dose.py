import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
import os


import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
import os

def write_dicom_dose(dose_data, output_path, image_data=None):
    """
    Write the dose array to a DICOM RT Dose file.

    Args:
        dose_data (dict): Dictionary containing dose data, dimensions, start, and width.
                          Required keys: 'data', 'start', 'width'.
        output_path (str): File path to save the DICOM RTDOSE file.
        image_data (dict, optional): Dictionary containing image and DICOM header information.
                                     Includes patientName, patientID, frameRefUID, etc.
    Returns:
        str: SOPInstanceUID of the saved DICOM file.
    """
    # Prepare DICOM metadata
    ds = FileDataset("", {}, file_meta=pydicom.Dataset(), preamble=b"\0" * 128)
    ds.Modality = "RTDOSE"
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.481.2"  # RTDOSE SOP Class UID
    ds.SOPInstanceUID = pydicom.uid.generate_uid()
    ds.InstanceCreationDate = datetime.now().strftime("%Y%m%d")
    ds.InstanceCreationTime = datetime.now().strftime("%H%M%S")

    # Add patient information from image_data
    if image_data:
        ds.PatientName = image_data.get("patientName", "Anonymous")
        ds.PatientID = image_data.get("patientID", "000000")
        ds.PatientBirthDate = image_data.get("patientBirthDate", "")
        ds.PatientSex = image_data.get("patientSex", "O")
        ds.FrameOfReferenceUID = image_data.get("frameRefUID", pydicom.uid.generate_uid())
        ds.StudyInstanceUID = image_data.get("studyUID", pydicom.uid.generate_uid())
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.StudyDescription = image_data.get("studyDescription", "RT Dose Study")
        ds.SeriesDescription = image_data.get("seriesDescription", "RT Dose Series")
    else:
        # Default placeholders if no image_data is provided
        ds.PatientName = "Anonymous"
        ds.PatientID = "000000"
        ds.PatientBirthDate = ""
        ds.PatientSex = "O"
        ds.FrameOfReferenceUID = pydicom.uid.generate_uid()
        ds.StudyInstanceUID = pydicom.uid.generate_uid()
        ds.SeriesInstanceUID = pydicom.uid.generate_uid()
        ds.StudyDescription = "RT Dose Study"
        ds.SeriesDescription = "RT Dose Series"

    # Add dose-specific metadata
    ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]  # Assuming HFS orientation
    ds.ImagePositionPatient = [
        dose_data["start"][0] * 10,
        dose_data["start"][1] * 10,
        dose_data["start"][2] * 10,
    ]
    ds.PixelSpacing = [dose_data["width"][0] * 10, dose_data["width"][1] * 10]
    ds.SliceThickness = dose_data["width"][2] * 10
    ds.Rows = dose_data["data"].shape[1]
    ds.Columns = dose_data["data"].shape[0]
    ds.NumberOfFrames = dose_data["data"].shape[2]
    ds.GridFrameOffsetVector = list(np.arange(0, ds.NumberOfFrames) * (-dose_data["width"][2] * 10))
    ds.DoseUnits = "GY"
    ds.DoseType = "PHYSICAL"
    ds.DoseSummationType = "PLAN"

    # Handle NaN and inf in dose data
    dose_data["data"] = np.nan_to_num(dose_data["data"], nan=0, posinf=0, neginf=0)

    # Set DoseGridScaling
    valid_data = dose_data["data"][~np.isnan(dose_data["data"]) & ~np.isinf(dose_data["data"])]
    ds.DoseGridScaling = np.max(valid_data) / 65535 if np.max(valid_data) > 0 else 1

    # Scale dose data
    scaled_data = np.clip(dose_data["data"] / ds.DoseGridScaling, 0, 65535).astype(np.uint16)
    ds.PixelData = scaled_data.tobytes()

    # Write the DICOM file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ds.save_as(output_path)
    print(f"DICOM RT Dose file saved to: {output_path}")

    return ds.SOPInstanceUID



# def write_dicom_dose(dose_data, output_path, dicom_info=None):
#     """
#     Write the dose array to a DICOM RT Dose file.
#
#     Args:
#         dose_data (dict): Dictionary containing dose data, dimensions, start, and width.
#                           Required keys: 'data', 'start', 'width'.
#         output_path (str): File path to save the DICOM RTDOSE file.
#         dicom_info (dict, optional): Dictionary containing additional DICOM header information.
#                                      Can include fields like patientName, patientID, frameRefUID, etc.
#
#     Returns:
#         str: SOPInstanceUID of the saved DICOM file.
#     """
#     try:
#         # Prepare DICOM metadata
#         ds = FileDataset("", {}, file_meta=pydicom.Dataset(), preamble=b"\0" * 128)
#         ds.Modality = "RTDOSE"
#         ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.481.2"  # RTDOSE SOP Class UID
#         ds.SOPInstanceUID = pydicom.uid.generate_uid()
#         ds.InstanceCreationDate = datetime.now().strftime("%Y%m%d")
#         ds.InstanceCreationTime = datetime.now().strftime("%H%M%S")
#
#         # Add patient information
#         if dicom_info:
#             ds.PatientName = dicom_info.get("patientName", "Anonymous")
#             ds.PatientID = dicom_info.get("patientID", "000000")
#             ds.PatientBirthDate = dicom_info.get("patientBirthDate", "")
#             ds.PatientSex = dicom_info.get("patientSex", "O")
#             ds.FrameOfReferenceUID = dicom_info.get("frameRefUID", pydicom.uid.generate_uid())
#
#         # Add dose-specific metadata
#         position = dicom_info.get("position", "HFS").upper() if dicom_info else "HFS"
#         if position == "HFP":
#             ds.ImageOrientationPatient = [-1, 0, 0, 0, -1, 0]
#         elif position == "FFS":
#             ds.ImageOrientationPatient = [-1, 0, 0, 0, 1, 0]
#         elif position == "FFP":
#             ds.ImageOrientationPatient = [1, 0, 0, 0, -1, 0]
#         else:  # Default to HFS
#             ds.ImageOrientationPatient = [1, 0, 0, 0, 1, 0]
#
#         # Calculate ImagePositionPatient based on orientation
#         ds.ImagePositionPatient = [
#             dose_data["start"][0] * 10 * ds.ImageOrientationPatient[0],
#             -(dose_data["start"][1] + dose_data["width"][1] * (dose_data["data"].shape[1] - 1)) * 10 * ds.ImageOrientationPatient[4],
#             -dose_data["start"][2] * 10 if ds.ImageOrientationPatient == [1, 0, 0, 0, 1, 0] else dose_data["start"][2] * 10,
#         ]
#
#         ds.PixelSpacing = [dose_data["width"][0] * 10, dose_data["width"][1] * 10]
#         ds.SliceThickness = dose_data["width"][2] * 10
#         ds.Rows = dose_data["data"].shape[1]
#         ds.Columns = dose_data["data"].shape[0]
#         ds.NumberOfFrames = dose_data["data"].shape[2]
#         ds.GridFrameOffsetVector = list(np.arange(0, ds.NumberOfFrames) * (-dose_data["width"][2] * 10))
#         ds.DoseUnits = "GY"
#         ds.DoseType = "PHYSICAL"
#
#         # Compute DoseGridScaling
#         dose_data["data"] = np.nan_to_num(dose_data["data"], nan=0, posinf=0, neginf=0)
#         max_dose = np.max(dose_data["data"])
#         if max_dose == 0:
#             raise ValueError("Dose data contains only zero values.")
#         ds.DoseGridScaling = max_dose / 65535
#
#         # Rotate and flip data for alignment
#         transformed_data = np.flip(np.rot90(dose_data["data"] / ds.DoseGridScaling, 3), 1).astype(np.uint16)
#         ds.PixelData = transformed_data.tobytes()
#
#         # Write the DICOM file
#         os.makedirs(os.path.dirname(output_path), exist_ok=True)
#         ds.save_as(output_path)
#         print(f"DICOM RT Dose file saved to: {output_path}")
#
#         return ds.SOPInstanceUID
#     except Exception as e:
#         print(f"Error writing DICOM dose: {e}")
#         raise
