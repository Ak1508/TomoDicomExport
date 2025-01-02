import os
import xml.etree.ElementTree as ET
import numpy as np

import os
import xml.etree.ElementTree as ET
import numpy as np


class LoadStructures:
    def __init__(self, xml_path, xml_name, image_data):
        self.xml_path = xml_path
        self.xml_name = xml_name
        self.image_data = image_data
        self.structures = []

    def parse_curve_file(self, file_path):
        """
        Parse the curve file as XML and extract contour data.

        Args:
            file_path (str): Path to the curve XML file.

        Returns:
            list: Extracted contour points or an empty list if parsing fails.
        """
        try:
            # Parse the XML file
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract points from the XML structure
            points_data = []
            point_elements = root.findall(".//pointData")
            for element in point_elements:
                num_data_points = int(element.get("numDataPoints", 0))
                if num_data_points > 0:
                    # Parse points into a list of tuples (x, y, z)
                    points_text = element.text.strip()
                    points = [
                        tuple(map(float, point.strip(";").split(",")))
                        for point in points_text.split("\n") if point
                    ]
                    points_data.append(points)

            return points_data
        except Exception as e:
            print(f"Error reading curve file {file_path}: {e}")
            return []

    def load_structures(self):
        """
        Load structures and associated masks based on the given image data.

        Returns:
            list: List of structures with metadata and masks.
        """
        # Parse the main XML file
        xml_file = os.path.join(self.xml_path, self.xml_name)
        if not os.path.exists(xml_file):
            raise FileNotFoundError(f"XML file not found: {xml_file}")

        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Find all troiList items
        troi_lists = root.findall(".//troiList/troiList")
        for troi in troi_lists:
            # Verify structure set UID
            parent_uid = troi.findtext("briefROI/dbInfo/databaseParent")
            if parent_uid != self.image_data.get("structureSetUID"):
                continue

            # Extract structure metadata
            structure = {
                "name": troi.findtext("briefROI/name", default="Unknown"),
                "color": {
                    "red": int(troi.findtext("briefROI/color/red", default="0")),
                    "green": int(troi.findtext("briefROI/color/green", default="0")),
                    "blue": int(troi.findtext("briefROI/color/blue", default="0")),
                },
                "isDensityOverridden": troi.findtext("briefROI/isDensityOverridden", default="False"),
                "overriddenDensity": float(troi.findtext("briefROI/overriddenDensity", default="0.0")),
                "filename": None,
                "mask": None,
                "volume": 0.0,
                "points": [],
            }

            # Locate the curve data file
            curve_file = troi.findtext("curveDataFile")
            if curve_file:
                structure["filename"] = os.path.join(self.xml_path, curve_file)

            # Parse curve file if available
            if structure["filename"] and os.path.exists(structure["filename"]):
                structure["points"] = self.parse_curve_file(structure["filename"])

            # If points exist, generate a mask
            if structure["points"]:
                structure["mask"] = self.generate_mask(structure["points"])
                structure["volume"] = self.calculate_volume(structure["mask"])

            self.structures.append(structure)

        return self.structures

    def generate_mask(self, points_data):
        """
        Generate a mask based on points data and the reference image dimensions.

        Args:
            points_data (list): List of contour points.

        Returns:
            np.ndarray: 3D mask array.
        """
        dimensions = self.image_data["dimensions"]
        mask = np.zeros(dimensions, dtype=bool)

        for points in points_data:
            # Assuming each points set corresponds to a single slice
            slice_index = int((points[0][2] - self.image_data["start"][2]) / self.image_data["width"][2])
            slice_mask = np.zeros(dimensions[:2], dtype=bool)

            # Convert points to pixel indices
            polygon = [
                ((point[0] - self.image_data["start"][0]) / self.image_data["width"][0],
                 (point[1] - self.image_data["start"][1]) / self.image_data["width"][1])
                for point in points
            ]
            polygon = np.round(polygon).astype(int)

            # Fill the polygon to generate the mask for the slice
            rr, cc = polygon[:, 0], polygon[:, 1]
            slice_mask[rr, cc] = True

            mask[:, :, slice_index] = slice_mask

        return mask

    def calculate_volume(self, mask):
        """
        Calculate the volume of the structure based on its mask.

        Args:
            mask (np.ndarray): 3D mask array.

        Returns:
            float: Volume in mm^3.
        """
        voxel_volume = np.prod(self.image_data["width"])
        return np.sum(mask) * voxel_volume


# if __name__ == "__main__":
#     # Example usage
#     # image_data = {
#     #     'structure_set_uid': 'some_uid',
#     #     'dimensions': (512, 512, 100),
#     #     'width': (0.5, 0.5, 0.5),
#     #     'start': (-128.0, -128.0, -50.0)
#     # }
#     from load_image import LoadImage
#
#     path = "Z:\Research\RADONC_S\Abishek\BILLER^LINDA R19431208.20230726.101950"
#     name = "BILLER^LINDA R_patient.xml"
#     plan_uid = "1.2.826.0.1.3680043.2.200.868841086.986.80371.127"
#
#     loader = LoadImage(path, name, plan_uid)
#     image_data = loader.load()
#     print(image_data['structureSetUID'])
#
#     st_loader = LoadStructures(path, name, image_data)
#     structures = st_loader.load_structures()
#     print(structures)
