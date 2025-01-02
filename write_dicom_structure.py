import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import datetime
import numpy as np

def write_dicom_structures(structures, file_path, dicom_header=None):
    """
    Writes a structure set to a DICOM RT Structure Set (RTSS) file.

    Args:
        structures (list): List of structures, each containing:
            - name (str): Name of the structure.
            - color (list): RGB color.
            - points (list of arrays): Points defining the structure.
        file_path (str): Path to save the DICOM RTSS file.
        dicom_header (dict, optional): DICOM header information including:
            - patientName, patientID, patientBirthDate, patientSex, patientAge,
              classUID, studyUID, seriesUID, frameRefUID, instanceUIDs, seriesDescription.

    Returns:
        str: SOPInstanceUID of the written RTSS file.
    """
    try:
        # Set current date and time
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")

        # Create a FileDataset instance for the RT Structure Set
        ds = FileDataset(file_path, {}, file_meta=Dataset(), preamble=b"\0" * 128)

        # File Meta Information
        ds.file_meta.FileMetaInformationVersion = b"\x00\x01"
        ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.481.3"
        ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
        ds.file_meta.TransferSyntaxUID = "1.2.840.10008.1.2"  # Implicit VR Little Endian
        ds.file_meta.ImplementationClassUID = "1.2.40.0.13.1.1"

        # SOP Instance Information
        ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID

        # Patient Information
        ds.PatientName = dicom_header.get("patientName", "DOE^John") if dicom_header else "DOE^John"
        ds.PatientID = dicom_header.get("patientID", "00000000") if dicom_header else "00000000"
        ds.PatientBirthDate = dicom_header.get("patientBirthDate", "") if dicom_header else ""
        ds.PatientSex = dicom_header.get("patientSex", "") if dicom_header else ""

        # Study and Series Information
        ds.StudyInstanceUID = dicom_header.get("studyUID", generate_uid()) if dicom_header else generate_uid()
        ds.SeriesInstanceUID = dicom_header.get("seriesUID", generate_uid()) if dicom_header else generate_uid()
        ds.FrameOfReferenceUID = dicom_header.get("frameRefUID", generate_uid()) if dicom_header else generate_uid()
        ds.SeriesDescription = dicom_header.get("seriesDescription", "Structure Set") if dicom_header else "Structure Set"
        ds.StructureSetLabel = dicom_header.get("structureLabel", "") if dicom_header else ""
        ds.StructureSetDate = date_str
        ds.StructureSetTime = time_str

        # Referenced Frame of Reference Sequence
        ds.ReferencedFrameOfReferenceSequence = []
        ref_frame_item = Dataset()
        ref_frame_item.FrameOfReferenceUID = ds.FrameOfReferenceUID
        ds.ReferencedFrameOfReferenceSequence.append(ref_frame_item)

        # Initialize ROI-related sequences
        ds.StructureSetROISequence = []
        ds.ROIContourSequence = []
        ds.RTROIObservationsSequence = []

        # Process each structure
        for i, structure in enumerate(structures):
            # Structure Set ROI Sequence
            roi_item = Dataset()
            roi_item.ROINumber = i + 1
            roi_item.ROIName = structure["name"]
            roi_item.ReferencedFrameOfReferenceUID = ds.FrameOfReferenceUID
            ds.StructureSetROISequence.append(roi_item)

            # ROI Contour Sequence
            contour_item = Dataset()
            contour_item.ReferencedROINumber = i + 1
            # contour_item.ROIDisplayColor = structure["color"]
            # # Replace this line in write_dicom_structures.py
            # contour_item.ROIDisplayColor = structure["color"]

            # Ensure color is converted from dictionary to list [R, G, B]
            if isinstance(structure["color"], dict) and {"red", "green", "blue"}.issubset(structure["color"].keys()):
                contour_item.ROIDisplayColor = [
                    int(structure["color"]["red"]),
                    int(structure["color"]["green"]),
                    int(structure["color"]["blue"]),
                ]
            else:
                raise ValueError(f"Invalid color format for structure: {structure['color']}")

            # # With this updated code
            # if isinstance(structure["color"], (list, tuple)) and len(structure["color"]) == 3:
            #     contour_item.ROIDisplayColor = [int(c) for c in structure["color"]]
            # else:
            #     raise ValueError(f"Invalid color format for structure: {structure['color']}")

            contour_item.ContourSequence = []

            for points in structure["points"]:
                contour_sequence_item = Dataset()
                contour_sequence_item.ContourGeometricType = "CLOSED_PLANAR"
                contour_sequence_item.NumberOfContourPoints = len(points)
                contour_sequence_item.ContourData = np.array(points).flatten().tolist()
                # contour_sequence_item.ContourData = points.flatten().tolist()
                contour_item.ContourSequence.append(contour_sequence_item)

            ds.ROIContourSequence.append(contour_item)

            # RT ROI Observations Sequence
            obs_item = Dataset()
            obs_item.ObservationNumber = i + 1
            obs_item.ReferencedROINumber = i + 1
            obs_item.RTROIInterpretedType = "ORGAN"
            ds.RTROIObservationsSequence.append(obs_item)

        # Save the DICOM file
        ds.is_little_endian = True
        ds.is_implicit_VR = True
        ds.save_as(file_path)

        print(f"DICOM RT Structure Set saved successfully to {file_path}")
        return ds.SOPInstanceUID

    except Exception as e:
        print(f"Error writing DICOM RT Structure Set: {e}")
        raise