import os
import xml.etree.ElementTree as ET
import numpy as np

class PlanLoader:
    def __init__(self, xml_path, xml_name, plan_uid):
        self.xml_path = xml_path
        self.xml_name = xml_name
        self.plan_uid = plan_uid
        self.plan_data = {}

    def parse_patient_demographics(self, root):
        # Extract patient information
        patient = root.find(".//patient/briefPatient")
        if patient is not None:
            self.plan_data['patient_name'] = patient.findtext('patientName', default="Unknown")
            self.plan_data['patient_id'] = patient.findtext('patientID', default="Unknown")
            self.plan_data['patient_birth_date'] = patient.findtext('patientBirthDate', default="Unknown")
            self.plan_data['patient_gender'] = patient.findtext('patientGender', default="Unknown")

    def validate_plan_uid(self, root):
        # Validate the plan UID and fetch plan details
        plans = root.findall(".//fullPlanDataArray/fullPlanDataArray/plan/briefPlan")
        for plan in plans:
            uid = plan.findtext("dbInfo/databaseUID")
            if uid == self.plan_uid:
                self.plan_data['plan_label'] = plan.findtext('planLabel', default="Unknown")
                self.plan_data['plan_date'] = plan.findtext('modificationTimestamp/date', default="Unknown")
                self.plan_data['plan_time'] = plan.findtext('modificationTimestamp/time', default="Unknown")
                return True
        return False

    def load_fluence_delivery_plan(self, root):
        # Load fluence delivery plan binary file paths and extract sinogram
        delivery_plans = root.findall(".//fullDeliveryPlanDataArray/fullDeliveryPlanDataArray")
        sinogram = []

        for plan in delivery_plans:
            uid = plan.findtext("deliveryPlan/dbInfo/databaseUID")
            if uid == self.plan_data.get('fluence_uid'):
                file_elements = plan.findall("binaryFileNameArray/binaryFileNameArray")
                for file_element in file_elements:
                    filename = file_element.text
                    file_path = os.path.join(self.xml_path, filename)
                    if os.path.exists(file_path):
                        sinogram.append(self.extract_sinogram(file_path))
                break

        if sinogram:
            self.plan_data['fluence_sinogram'] = np.hstack(sinogram)

    def extract_sinogram(self, file_path):
        # Extract binary data from a sinogram file
        try:
            with open(file_path, 'rb') as f:
                data = np.fromfile(f, dtype=np.float64)
                if data.size % 64 != 0:
                    print(f"Warning: Data size {data.size} is not divisible by 64. Trimming excess.")
                num_rows = data.size // 64
                data = data[:num_rows * 64]  # Trim excess elements
                return data.reshape(num_rows, 64)
        except Exception as e:
            print(f"Error reading sinogram file {file_path}: {e}")
            return np.array([])

    def load_machine_agnostic_plan(self, root):
        # Load machine-agnostic delivery plan
        delivery_plans = root.findall(".//fullDeliveryPlanDataArray/fullDeliveryPlanDataArray")
        agnostic_sinogram = []

        for plan in delivery_plans:
            purpose = plan.findtext("deliveryPlan/purpose")
            if purpose == "Machine_Agnostic":
                file_elements = plan.findall("binaryFileNameArray/binaryFileNameArray")
                for file_element in file_elements:
                    filename = file_element.text
                    file_path = os.path.join(self.xml_path, filename)
                    if os.path.exists(file_path):
                        agnostic_sinogram.append(self.extract_sinogram(file_path))
                break

        if agnostic_sinogram:
            self.plan_data['machine_agnostic_sinogram'] = np.hstack(agnostic_sinogram)

    def consistency_check(self):
        # Ensure fluence and machine-agnostic sinograms are compatible
        fluence_sinogram = self.plan_data.get('fluence_sinogram')
        agnostic_sinogram = self.plan_data.get('machine_agnostic_sinogram')

        if fluence_sinogram is not None and agnostic_sinogram is not None:
            if fluence_sinogram.shape != agnostic_sinogram.shape:
                print("Warning: Sinogram shapes do not match.")

    def load_plan(self):
        # Load XML and parse plan details
        xml_file = os.path.join(self.xml_path, self.xml_name)
        if not os.path.exists(xml_file):
            raise FileNotFoundError(f"XML file not found: {xml_file}")

        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Step 1: Parse patient demographics
        self.parse_patient_demographics(root)

        # Step 2: Validate plan UID
        if not self.validate_plan_uid(root):
            raise ValueError(f"Plan UID {self.plan_uid} not found in {self.xml_name}")

        # Step 3: Load fluence delivery plan
        self.load_fluence_delivery_plan(root)

        # Step 4: Load machine-agnostic plan
        self.load_machine_agnostic_plan(root)

        # Step 5: Perform consistency checks
        self.consistency_check()

        return self.plan_data


# if __name__ == "__main__":
#     path = "Z:\Research\RADONC_S\Abishek\BILLER^LINDA R19431208.20230726.101950"
#     name = "BILLER^LINDA R_patient.xml"
#     plan_uid = "1.2.826.0.1.3680043.2.200.868841086.986.80371.127"
#
#     # Example usage
#     # loader = PlanLoader("/path/to/xml", "patient.xml", "plan_uid")
#     # plan_data = loader.load_plan()
#     # print(plan_data)
#
#     try:
#         loader = PlanLoader(path, name, plan_uid)
#         plan_data = loader.load_plan()
#         print (plan_data)
#         # print(f"Patient Name: {plan_data.patientName}")
#         # print(f"Plan Label: {plan_data.planLabel}")
#         # print(f"Sinogram Data: {plan_data.sinogram[:10] if plan_data.sinogram else None}")
#     except Exception as e:
#         print(f"Error: {str(e)}")
#
#     # try:
#     #     plan_data = load_plan(path, name, plan_uid)
#     #     print(f"Patient Name: {plan_data.patientName}")
#     #     print(f"Plan Label: {plan_data.planLabel}")
#     #     print(f"Sinogram Data: {plan_data.sinogram[:10] if plan_data.sinogram else None}")
#     # except Exception as e:
#     #     print(f"Error: {str(e)}")
