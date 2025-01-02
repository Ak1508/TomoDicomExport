import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import datetime
import numpy as np


def write_dicom_tomo_plan(plan, file_path):
    """
    Writes a TomoTherapy plan to a DICOM RT Plan file.

    Args:
        plan (dict): Plan data containing patient and treatment information.
        file_path (str): Path to save the DICOM RT Plan file.

    Returns:
        str: SOPInstanceUID of the written RT Plan file.
    """
    try:
        # Set current date and time
        now = datetime.datetime.now()
        date_str = now.strftime("%Y%m%d")
        time_str = now.strftime("%H%M%S")

        # Create a FileDataset instance for the RT Plan
        ds = FileDataset(file_path, {}, file_meta=Dataset(), preamble=b"\0" * 128)

        # File Meta Information
        ds.file_meta.FileMetaInformationVersion = b"\x00\x01"
        ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.481.5"
        ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
        ds.file_meta.TransferSyntaxUID = "1.2.840.10008.1.2"  # Implicit VR Little Endian
        ds.file_meta.ImplementationClassUID = "1.2.40.0.13.1.1"

        # SOP Instance Information
        ds.SOPClassUID = ds.file_meta.MediaStorageSOPClassUID
        ds.SOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID

        # Patient Information
        ds.PatientName = plan.get("patientName", "DOE^John")
        ds.PatientID = plan.get("patientID", "00000000")
        ds.PatientBirthDate = plan.get("patientBirthDate", "")
        ds.PatientSex = plan.get("patientSex", "")

        # Study and Series Information
        ds.StudyInstanceUID = plan.get("studyUID", generate_uid())
        ds.SeriesInstanceUID = generate_uid()
        ds.FrameOfReferenceUID = plan.get("frameRefUID", generate_uid())
        ds.StudyDate = date_str
        ds.StudyTime = time_str
        ds.SeriesDescription = plan.get("seriesDescription", "TomoTherapy Plan")
        ds.StudyDescription = plan.get("studyDescription", "")

        # Plan Information
        ds.RTPlanLabel = plan.get("planLabel", "")
        ds.RTPlanGeometry = "PATIENT"
        ds.InstanceCreationDate = date_str
        ds.InstanceCreationTime = time_str

        # Prescription Information
        if "rxDose" in plan and "rxVolume" in plan:
            ds.PrescriptionDescription = (
                f"{plan['rxVolume']:.1f}% of the prescription volume receives at least {plan['rxDose']:.1f} Gy"
            )

        # Fraction Group Sequence
        if "fractions" in plan:
            fg_item = Dataset()
            fg_item.FractionGroupNumber = 1
            fg_item.NumberOfFractionsPlanned = plan["fractions"]
            fg_item.NumberOfBeams = 1
            fg_item.NumberOfBrachyApplicationSetups = 0
            if "rxDose" in plan:
                fg_item.ReferencedBeamSequence = [Dataset()]
                fg_item.ReferencedBeamSequence[0].BeamMeterset = 1
                fg_item.ReferencedBeamSequence[0].ReferencedBeamNumber = 1
                fg_item.ReferencedDoseReferenceSequence = [Dataset()]
                fg_item.ReferencedDoseReferenceSequence[0].TargetPrescriptionDose = plan["rxDose"]
            ds.FractionGroupSequence = [fg_item]

        # Beam Sequence
        if "machine" in plan and "planType" in plan:
            beam_item = Dataset()
            beam_item.Manufacturer = "TomoTherapy Incorporated"
            beam_item.ManufacturerModelName = "Hi-Art"
            beam_item.TreatmentMachineName = plan["machine"]
            beam_item.PrimaryDosimeterUnit = "MINUTE"
            beam_item.SourceAxisDistance = 850
            beam_item.BeamName = f"{plan['planType']} TomoTherapy Beam"
            beam_item.RadiationType = "PHOTON"
            beam_item.TreatmentDeliveryType = "TREATMENT"
            beam_item.NumberOfControlPoints = len(plan.get("controlPoints", []))

            # Control Points
            control_points = []
            for i, cp in enumerate(plan.get("controlPoints", [])):
                cp_item = Dataset()
                cp_item.ControlPointIndex = i
                cp_item.NominalBeamEnergy = 6
                cp_item.BeamLimitingDevicePositionSequence = [Dataset(), Dataset()]
                cp_item.BeamLimitingDevicePositionSequence[0].RTBeamLimitingDeviceType = "X"
                cp_item.BeamLimitingDevicePositionSequence[0].LeafJawPositions = [-200, 200]
                cp_item.BeamLimitingDevicePositionSequence[1].RTBeamLimitingDeviceType = "ASYMY"
                cp_item.BeamLimitingDevicePositionSequence[1].LeafJawPositions = cp.get("jaws", [-200, 200])
                cp_item.GantryAngle = cp.get("gantryAngle", 0)
                cp_item.IsocenterPosition = cp.get("isocenter", [0, 0, 0])
                cp_item.CumulativeMetersetWeight = cp.get("cumulativeWeight", 0)
                control_points.append(cp_item)

            beam_item.ControlPointSequence = control_points
            ds.BeamSequence = [beam_item]

        # Patient Setup Sequence
        if "position" in plan:
            ps_item = Dataset()
            ps_item.PatientPosition = plan["position"]
            ps_item.PatientSetupNumber = 1
            ds.PatientSetupSequence = [ps_item]

        # Referenced Structure Set
        if "structureSetUID" in plan:
            rss_item = Dataset()
            rss_item.ReferencedSOPClassUID = "1.2.840.10008.5.1.4.1.1.481.3"
            rss_item.ReferencedSOPInstanceUID = plan["structureSetUID"]
            ds.ReferencedStructureSetSequence = [rss_item]

        # Save the DICOM file
        ds.is_little_endian = True
        ds.is_implicit_VR = True
        ds.save_as(file_path)

        print(f"DICOM RT Plan saved successfully to {file_path}")
        return ds.SOPInstanceUID

    except Exception as e:
        print(f"Error writing DICOM RT Plan: {e}")
        raise
