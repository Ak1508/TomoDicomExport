import os
import xml.etree.ElementTree as ET
import numpy as np

class LoadPlanDose:
    def __init__(self, xml_path, xml_name, plan_uid):
        self.xml_path = xml_path
        self.xml_name = xml_name
        self.plan_uid = plan_uid
        self.dose = {}

    def load_dose(self):
        """
        Load the optimized dose after EOP (Final Dose) for a given plan UID.

        Returns:
            dict: Dose data and metadata.

        Raises:
            FileNotFoundError: If the XML file is not found.
            ValueError: If no matching dose data is found.
        """
        # Parse the main XML file
        xml_file = os.path.join(self.xml_path, self.xml_name)
        if not os.path.exists(xml_file):
            raise FileNotFoundError(f"XML file not found: {xml_file}")

        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Debugging: List all image types and their database parents
        print("Listing all image types and their database parents:")
        image_nodes = root.findall(".//fullImageDataArray/fullImageDataArray/image")
        checked_image_types = []
        checked_database_parents = []

        for node in image_nodes:
            image_type = node.findtext("imageType")
            database_parent = node.findtext("dbInfo/databaseParent")
            print(f"Image Type: {image_type}, Database Parent: {database_parent}")

            # print(ET.tostring(node, encoding="unicode"))

            checked_image_types.append(image_type)
            checked_database_parents.append(database_parent)
            # print(f"Image Type: {image_type}, Database Parent: {database_parent}")

            if image_type == "Opt_Dose_After_EOP" and database_parent == self.plan_uid:
                print(f"Matching dose found for plan UID: {self.plan_uid}")

                # Extract dose metadata
                self.dose["frameOfReference"] = node.findtext("frameOfReference")
                self.dose["filename"] = os.path.join(
                    self.xml_path, node.findtext("arrayHeader/binaryFileName"))
                self.dose["dimensions"] = [
                    int(node.findtext("arrayHeader/dimensions/x")),
                    int(node.findtext("arrayHeader/dimensions/y")),
                    int(node.findtext("arrayHeader/dimensions/z"))
                ]
                self.dose["start"] = [
                    float(node.findtext("arrayHeader/start/x")),
                    float(node.findtext("arrayHeader/start/y")),
                    float(node.findtext("arrayHeader/start/z"))
                ]
                self.dose["width"] = [
                    float(node.findtext("arrayHeader/elementSize/x")),
                    float(node.findtext("arrayHeader/elementSize/y")),
                    float(node.findtext("arrayHeader/elementSize/z"))
                ]

                # Load dose data from the binary file
                self._load_binary_data()
                return self.dose

        # Fallback: Search for plan trials if no dose found
        print("Searching for plan trials...")
        plan_trials = root.findall(".//patientPlanTrial")
        print("Listing all plan trials and their parents:")
        for trial in plan_trials:
            trial_uid = trial.findtext("dbInfo/databaseUID")
            parent_uid = trial.findtext("dbInfo/databaseParent")
            print(f"Plan Trial UID: {trial_uid}, Parent UID: {parent_uid}")
            # print(ET.tostring(trial, encoding="unicode"))

            if parent_uid == self.plan_uid:
                print(f"Plan trial found for parent UID: {parent_uid}")
                self._search_trial_dose(root, trial_uid)
                if self.dose:
                    return self.dose

        # Raise enhanced error if no dose found
        raise ValueError(
            f"No matching dose data found for plan UID {self.plan_uid}.\n"
            f"Checked Image Types: {checked_image_types}\n"
            f"Checked Database Parents: {checked_database_parents}\n"
            f"Expected Dose Type: 'Opt_Dose_After_EOP'."
        )

    def _search_trial_dose(self, root, trial_uid):
        """
        Search for dose data associated with a specific trial UID.

        Args:
            root: XML root element.
            trial_uid: Trial UID to search for.
        """
        dose_volumes = root.findall(".//doseVolumeList/doseVolumeList")
        for dose_volume in dose_volumes:
            # print(ET.tostring(dose_volume, encoding="unicode"))
            image_type = dose_volume.findtext("imageType")
            database_parent = dose_volume.findtext("dbInfo/databaseParent")

            if image_type == "Opt_Dose_After_EOP" and database_parent == trial_uid:
                print(f"Matching dose found for trial UID: {trial_uid}")

                # Extract dose metadata
                self.dose["frameOfReference"] = dose_volume.findtext("frameOfReference")
                self.dose["filename"] = os.path.join(self.xml_path, dose_volume.findtext("arrayHeader/binaryFileName"))
                self.dose["dimensions"] = [
                    int(dose_volume.findtext("arrayHeader/dimensions/x")),
                    int(dose_volume.findtext("arrayHeader/dimensions/y")),
                    int(dose_volume.findtext("arrayHeader/dimensions/z"))
                ]
                self.dose["start"] = [
                    float(dose_volume.findtext("arrayHeader/start/x")),
                    float(dose_volume.findtext("arrayHeader/start/y")),
                    float(dose_volume.findtext("arrayHeader/start/z"))
                ]
                self.dose["width"] = [
                    float(dose_volume.findtext("arrayHeader/elementSize/x")),
                    float(dose_volume.findtext("arrayHeader/elementSize/y")),
                    float(dose_volume.findtext("arrayHeader/elementSize/z"))
                ]

                # Load dose data from the binary file
                self._load_binary_data()

    def _load_binary_data(self):
        """
        Load the binary dose data into the dose dictionary.
        """
        if not os.path.exists(self.dose["filename"]):
            raise FileNotFoundError(f"Dose binary file not found: {self.dose['filename']}")

        with open(self.dose["filename"], "rb") as f:
            binary_data = np.fromfile(f, dtype=np.float32)
            self.dose["data"] = binary_data.reshape(self.dose["dimensions"])




# if __name__ == "__main__":
#     # Define test input
#     test_xml_path = "Z:\Research\RADONC_S\Abishek\BILLER^LINDA R19431208.20230726.101950"
#     test_file_name = "BILLER^LINDA R_patient.xml"
#     test_plan_uid = "1.2.826.0.1.3680043.2.200.868841086.986.80371.127"
#
#     # Call the function
#     loader = LoadPlanDose(test_xml_path, test_file_name, test_plan_uid)
#     dose_data = loader.load_dose()
#     print (dose_data)


