import os
import numpy as np
from lxml import etree
import logging
import matplotlib.pyplot as plt

class LoadImage:
    def __init__(self, xml_path, xml_name, plan_uid):
        """
        Initialize the LoadImage class.

        Args:
            xml_path (str): Path to the directory containing the XML file.
            xml_name (str): Name of the XML file.
            plan_uid (str): UID of the plan to extract the reference image.
        """
        self.xml_path = xml_path
        self.xml_name = xml_name
        self.plan_uid = plan_uid
        self.image = {
            "classUID": "1.2.840.10008.5.1.4.1.1.2",  # Standard UID
        }

    def extract_text(self, tree, xpath_query):
        """
        Extract text from the first node that matches the XPath query.

        Args:
            tree (etree.ElementTree): Parsed XML tree.
            xpath_query (str): XPath query string.

        Returns:
            str: Extracted text or None if no match is found.
        """
        nodes = tree.xpath(xpath_query)
        return nodes[0].text if nodes else None

    def parse_xml(self):
        """
        Parse the XML file and extract image-related information.

        Returns:
            dict: A dictionary containing the image data and metadata.
        """
        xml_file = os.path.join(self.xml_path, self.xml_name)
        if not os.path.exists(xml_file):
            raise FileNotFoundError(f"XML file {xml_file} does not exist.")

        tree = etree.parse(xml_file)

        # Extract patient demographics
        self.image["patientName"] = self.extract_text(tree, "//FullPatient/patient/briefPatient/patientName")
        self.image["patientID"] = self.extract_text(tree, "//FullPatient/patient/briefPatient/patientID")
        self.image["patientBirthDate"] = self.extract_text(tree, "//FullPatient/patient/briefPatient/patientBirthDate")
        self.image["patientSex"] = self.extract_text(tree, "//FullPatient/patient/briefPatient/patientGender")

        # Extract WL and WW from XML if present
        self.image["window_center"] = float(self.extract_text(tree, "//WindowCenter") or 0)
        self.image["window_width"] = float(self.extract_text(tree, "//WindowWidth") or 1000)

        # Find the plan matching the given plan UID
        plan_nodes = tree.xpath("//fullPlanDataArray/fullPlanDataArray")
        for plan_node in plan_nodes:
            plan_uid_node = plan_node.xpath("plan/briefPlan/dbInfo/databaseUID")
            if not plan_uid_node or plan_uid_node[0].text != self.plan_uid:
                continue

            # Extract IVDT
            ivdt_node = plan_node.xpath("plan/fullDoseIVDT")
            self.image["fullDoseIVDT"] = ivdt_node[0].text if ivdt_node else None

            # Extract patient position
            position_node = plan_node.xpath("plan/patientPosition")
            self.image["position"] = position_node[0].text if position_node else "Unknown"

            # Extract structure set UID
            structure_set_uid_node = plan_node.xpath("plan/planStructureSetUID")
            self.image["structureSetUID"] = structure_set_uid_node[0].text if structure_set_uid_node else None

            # Extract isocenter coordinates
            self.image["isocenter"] = [
                float(self.extract_text(tree, "//referenceImageIsocenter/x") or 0),
                float(self.extract_text(tree, "//referenceImageIsocenter/y") or 0),
                float(self.extract_text(tree, "//referenceImageIsocenter/z") or 0),
            ]

            # Extract couch information
            self.image["couchChecksum"] = self.extract_text(tree, "//couchChecksum")
            self.image["couchInsertionPosition"] = self.extract_text(tree, "//couchInsertionPosition")

            # Extract image data
            image_nodes = plan_node.xpath("fullImageDataArray/fullImageDataArray/image")
            for image_node in image_nodes:
                image_type_node = image_node.xpath("imageType")
                if not image_type_node or image_type_node[0].text not in ["KVCT", "Registered_MVCT"]:
                    continue

                # Extract filename
                filename_node = image_node.xpath("arrayHeader/binaryFileName")
                if filename_node:
                    self.image["filename"] = os.path.join(self.xml_path, filename_node[0].text)

                # Extract dimensions
                self.image["dimensions"] = [
                    int(image_node.xpath("arrayHeader/dimensions/x")[0].text),
                    int(image_node.xpath("arrayHeader/dimensions/y")[0].text),
                    int(image_node.xpath("arrayHeader/dimensions/z")[0].text),
                ]

                # Extract start coordinates
                self.image["start"] = [
                    float(image_node.xpath("arrayHeader/start/x")[0].text),
                    float(image_node.xpath("arrayHeader/start/y")[0].text),
                    float(image_node.xpath("arrayHeader/start/z")[0].text),
                ]

                # Extract voxel widths
                self.image["width"] = [
                    float(image_node.xpath("arrayHeader/elementSize/x")[0].text),
                    float(image_node.xpath("arrayHeader/elementSize/y")[0].text),
                    float(image_node.xpath("arrayHeader/elementSize/z")[0].text),
                ]

                # Extract scaling factors
                self.image["rescale_slope"] = float(self.extract_text(tree, "//RescaleSlope") or 1)
                self.image["rescale_intercept"] = float(self.extract_text(tree, "//RescaleIntercept") or -1024)

                break

        # Ensure the binary file exists
        if "filename" not in self.image or not os.path.exists(self.image["filename"]):
            raise FileNotFoundError(f"Binary file for plan UID {self.plan_uid} not found.")

    def load_binary_data(self):
        """
        Load binary image data from the file.

        Returns:
            dict: A dictionary containing image data and metadata.
        """
        with open(self.image["filename"], "rb") as f:
            image_data = np.fromfile(f, dtype=np.uint16)
            # print("First 100 raw values:", image_data[:100])
            self.image["data"] = image_data.reshape(self.image["dimensions"], order='F')

        # Convert the data to a floating-point type and apply scaling
        rescale_slope = self.image.get("rescale_slope", 1)
        rescale_intercept = self.image.get("rescale_intercept", -1024)
        print (rescale_slope, rescale_intercept)
        self.image["data"] = self.image["data"].astype(np.float32) * rescale_slope + rescale_intercept

        return self.image

    def load_image(self):
        """
        Load and process image data.

        Returns:
            dict: A dictionary containing the image data and metadata.
        """
        self.parse_xml()
        return self.load_binary_data()

def plot_image_slice(image_data, slice_index=0, orientation='axial'):
    """
    Plot a specific slice of the image data.

    Args:
        image_data (dict): The loaded image data and metadata.
        slice_index (int): The index of the slice to plot.
        orientation (str): Orientation of the slice ('axial', 'sagittal', 'coronal').
    """
    if orientation == 'axial':
        slice_data = image_data["data"][:, :, slice_index]
        extent = [
            image_data["start"][0],
            image_data["start"][0] + image_data["dimensions"][0] * image_data["width"][0],
            image_data["start"][1],
            image_data["start"][1] + image_data["dimensions"][1] * image_data["width"][1],
        ]
    elif orientation == 'sagittal':
        slice_data = image_data["data"][:, slice_index, :]
        extent = [
            image_data["start"][2],
            image_data["start"][2] + image_data["dimensions"][2] * image_data["width"][2],
            image_data["start"][1],
            image_data["start"][1] + image_data["dimensions"][1] * image_data["width"][1],
        ]
    elif orientation == 'coronal':
        slice_data = image_data["data"][slice_index, :, :]
        extent = [
            image_data["start"][0],
            image_data["start"][0] + image_data["dimensions"][0] * image_data["width"][0],
            image_data["start"][2],
            image_data["start"][2] + image_data["dimensions"][2] * image_data["width"][2],
        ]
    else:
        raise ValueError("Invalid orientation. Choose from 'axial', 'sagittal', or 'coronal'.")

    plt.figure(figsize=(8, 8))
    plt.imshow(np.flipud(slice_data.T), cmap="gray", origin="lower")
    # plt.colorbar(label="Pixel Intensity")
    plt.title(f"{orientation.capitalize()} Slice {slice_index}")
    plt.xlabel("Position (cm)")
    plt.ylabel("Position (cm)")
    plt.show()


#
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.INFO)
#
#     path = "Z:\Research\RADONC_S\Abishek\BILLER^LINDA R19431208.20230726.101950"
#     name = "BILLER^LINDA R_patient.xml"
#     plan_uid = "1.2.826.0.1.3680043.2.200.868841086.986.80371.127"
#
#     loader = LoadImage(path, name, plan_uid)
#     image_data = loader.load_image()
#     logging.info("Image data loaded successfully.")
#
#     print (image_data.keys())
#
#     print ("Dimension :", image_data['data'].shape)
#
#     print ("Width :", image_data['width'])
#     print ('Start :', image_data['start'])
#     print ("position :", image_data['position'])
#     print ('Window :', image_data['window_center'])
#
#     # plot to test
#     plot_image_slice(image_data, slice_index=50, orientation='axial')


