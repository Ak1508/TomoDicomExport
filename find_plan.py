import os
import xml.etree.ElementTree as ET


class PlanFinder:
    """
    Class to handle finding approved plans from a TomoTherapy patient archive XML file.
    """

    def __init__(self, xml_path, file_name):
        """
        Initialize the PlanFinder.

        Args:
            xml_path (str): Path to the directory containing the XML file.
            file_name (str): Name of the XML file.
        """
        self.xml_path = xml_path
        self.file_name = file_name
        self.full_path = os.path.join(xml_path, file_name)

        if not os.path.exists(self.full_path):
            raise FileNotFoundError(f"XML file not found: {self.full_path}")

        self.tree = ET.parse(self.full_path)
        self.root = self.tree.getroot()

    def find_all_plans(self, plan_type=None):
        """
        Find all plans in the XML file (approved and non-approved).

        Args:
            plan_type (str, optional): Restrict plans to a specific delivery type (e.g., "Helical").

        Returns:
            list: List of tuples where each tuple contains (UID, label, approved) for all plans.
        """
        print(f"Searching for all plans in {self.file_name}...")

        plans = []  # This will store all the found plans

        for plan in self.root.findall(".//fullPlanDataArray/fullPlanDataArray/plan/briefPlan"):
            # Extract various details for each plan
            db_uid = plan.findtext("dbInfo/databaseUID", default="Unknown UID")
            plan_label = plan.findtext("planLabel", default="Unknown Label")
            type_of_plan = plan.findtext("typeOfPlan",
                                         default="Unknown Type")  # Type of plan (e.g., Composite, PATIENT)

            # Debug: Print the details of the plan
            print(f"Plan UID: {db_uid}")
            print(f"Plan Label: {plan_label}")
            print(f"Type of Plan: {type_of_plan}")

            # Extract approval status
            approved_uid = plan.find("approvedPlanTrialUID")
            if approved_uid is not None:
                print("Approved Plan UID:", approved_uid.text)
            else:
                print("Approved Plan UID: Not Available")

            approved_status = (
                    approved_uid is not None
                    and approved_uid.text not in ["", "* * * DO NOT CHANGE THIS STRING VALUE * * *"]
            )

            # Extract delivery type if plan_type is provided
            if plan_type:
                delivery_type = plan.find("planDeliveryType")
                if delivery_type is not None:
                    print("Delivery Type:", delivery_type.text)
                else:
                    print("Delivery Type: Not Available")

                # Filter by plan_type
                if delivery_type is None or delivery_type.text != plan_type:
                    continue

            # Additional Debug: Check for plan type node
            plan_type_node = plan.find("typeOfPlan")
            if plan_type_node is not None:
                print("Plan Type Node:", plan_type_node.text)
            else:
                print("Plan Type Node: Not Available")

            # Filter for patient plans if necessary
            if plan_type_node is None or plan_type_node.text != "PATIENT":
                continue

            # Re-confirm db_uid and plan_label for valid plans
            db_uid = plan.find("dbInfo/databaseUID")
            plan_label = plan.find("planLabel")

            if db_uid is None or not db_uid.text:
                print(f"Skipping plan: Missing UID for Plan Label '{plan_label.text if plan_label else 'UNK'}'")
                continue
            print ("- -" *50)
            # Append plans with approval status
            plans.append((
                db_uid.text,  # Plan UID
                plan_label.text if plan_label is not None else "UNK",  # Plan Label
                approved_status  # Approved status (True/False)
            ))

        print(f"Found {len(plans)} plans." if plans else "No plans found.")
        return plans

    def find_plans(self, plan_type=None):
        """
        Find approved plans in the XML file.

        Args:
            plan_type (str, optional): Restrict plans to a specific delivery type (e.g., "Helical").

        Returns:
            list: List of tuples where each tuple contains (UID, label) for approved plans.
        """
        print(f"Searching for approved plans in {self.file_name}...")

        plans = []
        for plan in self.root.findall(".//fullPlanDataArray/fullPlanDataArray/plan/briefPlan"):

            approved_uid = plan.find("approvedPlanTrialUID")
            if approved_uid is None or approved_uid.text in ["", "* * * DO NOT CHANGE THIS STRING VALUE * * *"]:
                continue

            if plan_type:
                delivery_type = plan.find("planDeliveryType")
                if delivery_type is None or delivery_type.text != plan_type:
                    continue

            plan_type_node = plan.find("typeOfPlan")
            if plan_type_node is None or plan_type_node.text != "PATIENT":
                continue

            db_uid = plan.find("dbInfo/databaseUID")
            plan_label = plan.find("planLabel")

            if db_uid is None or not db_uid.text:
                continue

            plans.append((db_uid.text, plan_label.text if plan_label is not None else "UNK"))

        print(f"Found {len(plans)} approved plans." if plans else "No approved plans found.")
        return plans

    def handle_find_plans_results(self, plans):
        """
        Handle the result of finding plans.

        Args:
            plans (list): List of tuples (UID, label) for approved plans.

        Returns:
            str: The first plan UID if found, else None.
        """
        if not plans:
            print("No approved plans were found in the provided archive.")
            return None

        print(f"Found {len(plans)} approved plans. Selecting the first plan.")
        selected_plan_uid = plans[0][0]
        print(f"Selected Plan UID: {selected_plan_uid}")
        return selected_plan_uid

    def find_legacy_plans(self):
        """
        Find approved plans in legacy archives.

        Returns:
            list: A list of approved plan UIDs.
        """
        print("Searching for approved legacy plans...")

        approved_plans = []
        for plan in self.root.findall(".//legacyPlan"):
            approval_status = plan.findtext("approvalStatus")
            if approval_status and approval_status.lower() == "approved":
                plan_uid = plan.findtext("dbInfo/databaseUID")
                if plan_uid:
                    approved_plans.append(plan_uid)

        if not approved_plans:
            raise ValueError("No approved plans found in the legacy archive.")

        print(f"Found {len(approved_plans)} approved legacy plans.")
        return approved_plans


if __name__ == "__main__":
    xml_path = r'C:\Users\jjw3ax\Downloads\DicomConverter\CHRISTOPHER^CASSANDRA.20140411\CHRISTOPHER^CASSANDRA.20140411.084758'
    # "Z:\\Research\\RADONC_S\\Abishek\\BILLER^LINDA R19431208.20230726.101950"
    file_name = r'CHRISTOPHER^CASSANDRA_patient.xml'
    # "BILLER^LINDA R_patient.xml"

    finder = PlanFinder(xml_path, file_name)

    ### Checking for all plans
    plansList = finder.find_all_plans('Helical')

    # print (plansList)

    # print (finder)

#     # Find plans with an optional filter
#     plans = finder.find_plans(plan_type="Helical")
#     for uid, label in plans:
#         print(f"UID: {uid}, Label: {label}")
# #
#     # Handle the result of find_plans
#     planslist = finder.handle_find_plans_results(plans)
#     print (planslist)
#
#     # Find legacy plans
#     try:
#         legacy_plans = finder.find_legacy_plans()
#         for uid in legacy_plans:
#             print(f"Legacy Plan UID: {uid}")
#     except ValueError as e:
#         print(e)
