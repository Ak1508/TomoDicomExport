import glob
from lxml import etree

# Define the directory and file pattern
directory = r"Z:\Research\RADONC_S\Abishek\BILLER^LINDA R19431208.20230726.101950"
file_pattern = "*_machine.xml"

# Search for the file
matching_files = glob.glob(f"{directory}\\{file_pattern}")
if not matching_files:
    raise FileNotFoundError(f"No files matching the pattern '{file_pattern}' found in '{directory}'")
if len(matching_files) > 1:
    raise ValueError(f"Multiple files matching the pattern '{file_pattern}' found in '{directory}'. Please ensure only one file matches.")

# Parse the XML file
xml_file = matching_files[0]  # Use the first (and only) match
print(f"Using XML file: {xml_file}")

tree = etree.parse(xml_file)
print (tree)

# Perform XPath queries
root = tree.getroot()
print (root)

print(etree.tostring(root, pretty_print=True).decode())


# machine_id = root.xpath("//machine/id/text()")
# print(f"Machine ID: {machine_id[0] if machine_id else 'Not Found'}")



# from lxml import etree
#
# # Load the XML file
# xml_file = "Z:\Research\RADONC_S\Abishek\BILLER^LINDA R19431208.20230726.101950/*_machine.xml"  # Replace with your XML file
# tree = etree.parse(xml_file)
#
# # Create an XPath evaluator
# root = tree.getroot()

# # Use XPath to find elements
# machine_id = root.xpath("//machine/id/text()")
# machine_name = root.xpath("//machine/name/text()")
# machine_model = root.xpath("//machine/model/text()")
#
# # Print the results
# print(f"Machine ID: {machine_id[0] if machine_id else 'Not Found'}")
# print(f"Machine Name: {machine_name[0] if machine_name else 'Not Found'}")
# print(f"Machine Model: {machine_model[0] if machine_model else 'Not Found'}")
