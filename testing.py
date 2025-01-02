


import pydicom
import numpy as np

dicom_file = "Z:\\Research\\RADONC_S\\Abishek\\test\Dose\\RTDose.dcm"
ds = pydicom.dcmread(dicom_file)

print (ds)


print("Patient Name:", ds.get("PatientName", "Unknown"))
print("Patient ID:", ds.get("PatientID", "Unknown"))
# print("Study Instance UID:", ds.get("StudyInstanceUID", "Unknown"))
# print("Series Instance UID:", ds.get("SeriesInstanceUID", "Unknown"))
# print("Slice Thickness:", ds.get("SliceThickness", "Unknown"))
# print("Pixel Spacing:", ds.get("PixelSpacing", "Unknown"))
# print("Rows:", ds.Rows)
# print("Columns:", ds.Columns)
#
# if hasattr(ds, "PixelData"):
#     pixel_data = ds.pixel_array
#     print("Pixel Data Shape:", pixel_data.shape)
#     print("Pixel Value Range:", np.min(pixel_data), "-", np.max(pixel_data))
# else:
#     print("No Pixel Data found.")

# import xml.etree.ElementTree as ET
#
#
# def find_scaling_tags(file_path):
#     """
#     Parse XML file and look for scaling-related metadata such as Rescale Slope and Intercept.
#     """
#     try:
#         # Parse the XML file
#         tree = ET.parse(file_path)
#         root = tree.getroot()
#
#         rescale_slope = root.find(".//ImageAttributes/Scaling/RescaleSlope")
#         rescale_intercept = root.find(".//ImageAttributes/Scaling/RescaleIntercept")
#
#         print (rescale_intercept, rescale_slope)
#     except:
#
#         print ("No Result")
#
#     #     # Keywords to search for
#     #     scaling_keywords = ["Rescale", "Slope", "Intercept", "Scaling", "Transform", "PixelValue"]
#     #
#     #     # Store results
#     #     scaling_info = {}
#     #
#     #     # Search for tags and attributes containing scaling-related information
#     #     for element in root.iter():
#     #         # Check tag name for scaling keywords
#     #         if any(keyword in element.tag for keyword in scaling_keywords):
#     #             try:
#     #                 # Parse numeric value
#     #                 scaling_info[element.tag] = float(element.text.strip())
#     #             except (ValueError, AttributeError):
#     #                 pass
#     #
#     #         # Check attributes for scaling keywords
#     #         for attr_name, attr_value in element.attrib.items():
#     #             if any(keyword in attr_name for keyword in scaling_keywords):
#     #                 try:
#     #                     scaling_info[attr_name] = float(attr_value.strip())
#     #                 except ValueError:
#     #                     scaling_info[attr_name] = attr_value  # Store as-is if not numeric
#     #
#     #     return scaling_info if scaling_info else "No scaling-related metadata found."
#     #
#     # except Exception as e:
#     #     return f"Error parsing XML: {e}"
#
# def print_all_tags(file_path):
#     """
#     Prints all tags and their hierarchy in an XML file.
#     """
#     tree = ET.parse(file_path)
#     root = tree.getroot()
#
#     def recursive_print(element, level=0):
#         # Tags to exclude
#         exclude_tags = {"graphicData", "slicesToReconstruct", "scanListZValues", "scanList"}
#
#         # Skip excluded tags
#         if element.tag in exclude_tags:
#             return
#
#         # Print current tag and its text
#         print("---> " * level + f"Tag: {element.tag}, Text: {element.text.strip() if element.text else 'None'}")
#
#         # Recursively print child elements
#         for child in element:
#             recursive_print(child, level + 1)
#
#     # def recursive_print(element, level=0):
#     #     print("---> " * level + f"Tag: {element.tag}, Text: {element.text.strip() if element.text else 'None'}")
#     #     # for attr, value in element.attrib.items():
#     #     #     print("  " * (level + 1) + f"Attribute: {attr}, Value: {value}")
#     #     for child in element:
#     #         recursive_print(child, level + 1)
#
#     recursive_print(root)
#
# file_path = "Z:\\Research\\RADONC_S\\Abishek\\BILLER^LINDA R19431208.20230726.101950\\BILLER^LINDA R_patient.xml"
#
# print_all_tags(file_path)

