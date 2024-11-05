from xmlschema.validators.exceptions import XMLSchemaValidationError
from lxml import etree
from xmlschema.validators.schemas import *
from annotated_tree import annotate_tree_with_validation
import re

def parse_with_line_numbers(xml_file):
    """
    Parse an XML file and create a mapping of elements, subnodes, text nodes,
    and attributes to their line numbers, using XPath paths as keys.
    Returns the tree and a dictionary of line numbers.
    """
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(xml_file, parser)

    # Initialize line numbers dictionary
    line_numbers = {}

    # Function to get the XPath path of an element
    def get_element_path(element):
        return tree.getpath(element)

    # Recursive function to traverse all nodes, including attributes and text
    def traverse_element(element):
        # Store line number for the element itself
        element_path = get_element_path(element)
        line_numbers[element_path] = element.sourceline

        # Store line numbers for each attribute if available
        for name, value in element.attrib.items():
            attribute_path = f"{element_path}/@{name}"
            line_numbers[attribute_path] = element.sourceline  # Use XPath for attributes

        # Traverse children recursively
        for child in element:
            traverse_element(child)
        
        # If the element has a tail (text after the element's closing tag), store it
        if element.tail and element.sourceline:
            tail_path = f"{element_path}/tail"
            line_numbers[tail_path] = element.sourceline

    # Start traversal from the root
    root = tree.getroot()
    traverse_element(root)

    return tree, line_numbers


def validate_enhanced(self, source: Union[XMLSourceType, XMLResource],
              path: Optional[str] = None,
              schema_path: Optional[str] = None,
              use_defaults: bool = True,
              namespaces: Optional[NamespacesType] = None,
              max_depth: Optional[int] = None,
              extra_validator: Optional[ExtraValidatorType] = None,
              validation_hook: Optional[ValidationHookType] = None,
              allow_empty: bool = True,
              use_location_hints: bool = False,
              output_file: str = "validation_errors.log",
              modified_output_file: str = "modified_source.xml") -> None:
    """
    Validates XML data against the XSD schema/component instance, saving errors
    to an output file and generating a modified XML with validation status indicators.
    
    :param source: the source of XML data.
    :param path: optional XPath expression that matches elements of the XML data.
    :param schema_path: alternative XPath expression to select the XSD element.
    :param use_defaults: Use schema's default values for filling missing data.
    :param namespaces: optional mapping from namespace prefix to URI.
    :param max_depth: maximum level of validation.
    :param extra_validator: optional function for non-standard validations.
    :param validation_hook: optional function for stopping or changing validation.
    :param allow_empty: if False, generates a validation error for empty selections.
    :param use_location_hints: set to True to activate dynamic schema loading.
    :param output_file: file to save encountered errors.
    :param modified_output_file: file to save modified XML with validation status.
    """
    namespaces = namespaces or {}
    errors = []
    error_paths = set()  # Store specific element paths that contain validation errors
    missing_elements = {}  # Store missing elements with their parent paths
    unexpected_elements = {}  # Store unexpected elements with their paths and expected tags
    missing_attributes = {}  # Store missing attributes with their element paths
    not_allowed_attributes = {}  # Store not allowed attributes with their element paths

    # Parse the XML and get line numbers dictionary
    tree, line_numbers = parse_with_line_numbers(source)

    
    # Iterate over errors without raising them and identify specific elements
    for error in self.iter_errors(tree, path, schema_path, use_defaults,
                                  namespaces, max_depth, extra_validator,
                                  validation_hook, allow_empty, use_location_hints,
                                  validation='lax'):
        errors.append(str(error))
        
        if error.elem is not None:
            # Get the XPath of the error element
            element_path = tree.getpath(error.elem)

            # Check if the error message refers to an unexpected child with a specific tag
            unexpected_tag_match = re.search(r"Unexpected child with tag '(.+?)' at position \d+\. Tag '(.*?)' expected|Unexpected child with tag '(.+?)' at position \d+\. Tag \(([^)]+)\) expected|Unexpected child with tag '(.+?)' at position \d+\.", str(error))
            missing_element_match = re.search(r"is not complete\. Tag '(.*?)' expected|is not complete\. Tag \(([^)]+)\) expected", str(error))
            missing_attribue_match = re.search(r"missing required attribute '(.*?)'", str(error))
            not_allowed_attribute_match = re.search(r"'(.*?)' attribute not allowed", str(error))

            if unexpected_tag_match:

                unexpected_tag = unexpected_tag_match.group(1) or unexpected_tag_match.group(3) or unexpected_tag_match.group(5)
                expected_tags = []
                # Determine if we have a single expected tag or multiple tags
                if unexpected_tag_match.group(2):  # Single tag case
                    expected_tags = [unexpected_tag_match.group(2)]
                elif unexpected_tag_match.group(4):  # Multiple tags case
                    expected_tags = [tag.strip().strip("'") for tag in unexpected_tag_match.group(4).split('|')]

                # Manually search for this child element within the parent element
                for child in error.elem.iterchildren():
                    # Get the XPath path of the specific child element
                    child_path = tree.getpath(child)
                    if re.search(rf"{re.escape(unexpected_tag)}(\[\d+\])?$", child_path):  # Match the tag name without namespaces
                        error_paths.add(child_path)
                        break
                
                if child_path not in unexpected_elements:
                    unexpected_elements[child_path] = []
                # Append the expected tag to the list
                if expected_tags:
                    unexpected_elements[child_path].extend([unexpected_tag, expected_tags])
                else:
                    unexpected_elements[child_path].append(unexpected_tag)

            else:
                # Add the element's path to error paths if no unexpected child error is detected
                error_paths.add(element_path)

            if missing_element_match:
                if missing_element_match.group(1):  # Single tag case
                    missing_tags = [missing_element_match.group(1)]
                elif missing_element_match.group(2):  # Multiple tags case
                    missing_tags = [tag.strip().strip("'") for tag in missing_element_match.group(2).split('|')]
                # Extract the expected tag name from the error message
                if element_path not in missing_elements:
                    missing_elements[element_path] = []
                # Append the missing tag to the list
                missing_elements[element_path].extend(missing_tags)
            if missing_attribue_match:
                # Extract the missing attribute name from the error message
                missing_attribute = missing_attribue_match.group(1)
                # Add the attribute's path to missing attributes
                if element_path not in missing_attributes:
                    missing_attributes[element_path] = []
                missing_attributes[element_path].append(missing_attribute)

            if not_allowed_attribute_match:
                # Extract the not allowed attribute name from the error message
                not_allowed_attribute = not_allowed_attribute_match.group(1)
                # Add the attribute's path to not allowed attributes
                if element_path not in not_allowed_attributes:
                    not_allowed_attributes[element_path] = []
                not_allowed_attributes[element_path].append(not_allowed_attribute)
                
    # Log errors to the specified output file
    if errors:
        with open(output_file, "w") as f:
            for err in errors:
                f.write(f"{err}\n")

    # Annotate the tree with validation status
    annotate_tree_with_validation(tree, error_paths, missing_elements, missing_attributes, not_allowed_attributes, unexpected_elements)

    # Save the modified XML tree to the output file
    tree.write(modified_output_file, encoding="utf-8", xml_declaration=True, pretty_print=True)

