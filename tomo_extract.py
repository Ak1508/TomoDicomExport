import os
from load_image import LoadImage
from load_structure import LoadStructures
from load_plan_dose import LoadPlanDose
from load_plan import PlanLoader
from find_plan import PlanFinder
from write_dicom_tomo_plan import write_dicom_tomo_plan
from write_dicom_structure import write_dicom_structures
from write_dicom_image import write_dicom_image
from write_dicom_dose import write_dicom_dose

class TomoExtract:
    def __init__(self, xml_path, xml_name):
        """
        Initialize the TomoExtract class.

        Args:
            xml_path (str): Path to the directory containing the XML file.
            xml_name (str): Name of the XML file.
        """
        self.xml_path = xml_path
        self.xml_name = xml_name

    def find_approved_plans(self, plan_type=None):
        """
        Find approved plans in the provided XML archive.

        Args:
            plan_type (str, optional): Restrict to specific delivery type (e.g., "Helical").

        Returns:
            list: A list of approved plan UIDs and labels.
        """
        finder = PlanFinder(self.xml_path, self.xml_name)
        return finder.find_plans(plan_type)

    def load_plan_data(self, plan_uid):
        """
        Load all relevant plan data for a given UID.

        Args:
            plan_uid (str): UID of the plan to load.

        Returns:
            dict: A dictionary containing image, structure, plan, and dose data.
        """
        # Load image data
        image_loader = LoadImage(self.xml_path, self.xml_name, plan_uid)
        image_data = image_loader.load_image()

        # Load structure data
        structure_loader = LoadStructures(self.xml_path, self.xml_name, image_data)
        structure_data = structure_loader.load_structures()

        # Load plan data
        plan_loader = PlanLoader(self.xml_path, self.xml_name, plan_uid)
        plan_data = plan_loader.load_plan()

        # Load dose data
        dose_loader = LoadPlanDose(self.xml_path, self.xml_name, plan_uid)
        dose_data = dose_loader.load_dose()

        return {
            "image": image_data,
            "structures": structure_data,
            "plan": plan_data,
            "dose": dose_data
        }
    def export_dicom(self, plan_uid, export_path):
        """
        Export the loaded plan data to DICOM format.

        Args:
            plan_uid (str): UID of the plan to export.
            export_path (str): Path to save the DICOM files.
        """
        plan_data = self.load_plan_data(plan_uid)

        # Create directories for DICOM files
        rtplan_path = os.path.join(export_path, "RTPlan")
        rtstruct_path = os.path.join(export_path, "RTStruct")
        ct_path = os.path.join(export_path, "CT")
        dose_path = os.path.join(export_path, "Dose")

        os.makedirs(rtplan_path, exist_ok=True)
        os.makedirs(rtstruct_path, exist_ok=True)
        os.makedirs(ct_path, exist_ok=True)
        os.makedirs(dose_path, exist_ok=True)

        # Export RT Plan
        rtplan_file = os.path.join(rtplan_path, "RTPlan.dcm")
        write_dicom_tomo_plan(plan_data["plan"], rtplan_file)

        # Export RT Structures
        rtstruct_file = os.path.join(rtstruct_path, "RTStruct.dcm")
        write_dicom_structures(
            plan_data["structures"],
            rtstruct_file,
            plan_data["plan"]
        )

        # Export CT Images
        ct_prefix = os.path.join(ct_path, "CT")
        write_dicom_image(
            plan_data["image"],
            ct_prefix,
            plan_data["plan"]
        )

        # Export Dose
        dose_file = os.path.join(dose_path, "RTDose.dcm")

        write_dicom_dose(
            dose_data=plan_data["dose"],
            output_path=dose_file,
            image_data=plan_data['image']
        )
        print(f"Dose exported to: {dose_file}")


    # def export_dicom(self, plan_uid, export_path):
    #     """
    #     Export the loaded plan data to DICOM format.
    #
    #     Args:
    #         plan_uid (str): UID of the plan to export.
    #         export_path (str): Path to save the DICOM files.
    #     """
    #     plan_data = self.load_plan_data(plan_uid)
    #
    #     # Create directories for DICOM files
    #     rtplan_path = os.path.join(export_path, "RTPlan")
    #     rtstruct_path = os.path.join(export_path, "RTStruct")
    #     ct_path = os.path.join(export_path, "CT")
    #
    #
    #     os.makedirs(rtplan_path, exist_ok=True)
    #     os.makedirs(rtstruct_path, exist_ok=True)
    #     os.makedirs(ct_path, exist_ok=True)
    #
    #     # Export RT Plan
    #     rtplan_file = os.path.join(rtplan_path, "RTPlan.dcm")
    #     write_dicom_tomo_plan(plan_data["plan"], rtplan_file)
    #
    #     # Export RT Structures
    #     rtstruct_file = os.path.join(rtstruct_path, "RTStruct.dcm")
    #     write_dicom_structures(
    #         plan_data["structures"],
    #         rtstruct_file,
    #         plan_data["plan"]
    #     )
    #
    #     # Export CT Images
    #     ct_prefix = os.path.join(ct_path, "CT")
    #     write_dicom_image(
    #         plan_data["image"],
    #         ct_prefix,
    #         plan_data["plan"]
    #     )

    # def export_dicom(self, plan_uid, export_path):
    #     """
    #     Export the loaded plan data to DICOM format.
    #
    #     Args:
    #         plan_uid (str): UID of the plan to export.
    #         export_path (str): Path to save the DICOM files.
    #     """
    #     plan_data = self.load_plan_data(plan_uid)
    #
    #     # Create directories for DICOM files
    #     rtplan_path = os.path.join(export_path, "RTPlan")
    #     rtstruct_path = os.path.join(export_path, "RTStruct")
    #     os.makedirs(rtplan_path, exist_ok=True)
    #     os.makedirs(rtstruct_path, exist_ok=True)
    #
    #     # Export RT Plan
    #     rtplan_file = os.path.join(rtplan_path, "RTPlan.dcm")
    #     write_dicom_tomo_plan(plan_data["plan"], rtplan_file)
    #
    #     # Export RT Structures
    #     rtstruct_file = os.path.join(rtstruct_path, "RTStruct.dcm")
    #     write_dicom_structures(
    #         plan_data["structures"],
    #         rtstruct_file,
    #         plan_data["plan"]
    #     )

    # def export_dicom(self, plan_uid, export_path):
    #     """
    #     Export the DICOM files for the specified plan UID.
    #
    #     Args:
    #         plan_uid (str): UID of the plan to export.
    #         export_path (str): Directory to save the exported DICOM files.
    #
    #     Returns:
    #         None
    #     """
    #     # Load plan data
    #     plan_data = self.load_plan_data(plan_uid)
    #
    #     # Create export directories
    #     rtplan_dir = os.path.join(export_path, "RTPlan")
    #     os.makedirs(rtplan_dir, exist_ok=True)
    #
    #     # Export RTPlan
    #     rtplan_file = os.path.join(rtplan_dir, "RTPlan.dcm")
    #     write_dicom_tomo_plan(plan_data["plan"], rtplan_file)
    #
    #     print(f"RTPlan exported to: {rtplan_file}")

if __name__ == "__main__":
    # Example usage
    xml_path = "Z:\\Research\\RADONC_S\\Abishek\\BILLER^LINDA R19431208.20230726.101950"
    xml_name = "BILLER^LINDA R_patient.xml"

    tomo = TomoExtract(xml_path, xml_name)

    # Find approved plans
    approved_plans = tomo.find_approved_plans(plan_type="Helical")
    print("Approved Plans:", approved_plans)

    if approved_plans:
        # Load data for the first approved plan
        plan_uid = approved_plans[0][0]
        plan_data = tomo.load_plan_data(plan_uid)

        export_path = "Z:\\Research\\RADONC_S\\Abishek\\test"

        print("Plan Data:")
        # tomo.export_dicom(plan_uid, export_path)
        print("Image:", plan_data.keys())
        # print("Structures:", plan_data["structures"])
        # print("Plan:", plan_data["plan"])
        # print("Dose:", plan_data["dose"])
