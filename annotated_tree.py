from xmlschema.validators.exceptions import XMLSchemaValidationError
from xmlschema.validators.schemas import *

def annotate_tree_with_validation(tree, error_paths, missing_elements, missing_attributes, not_allowed_attributes, unexpected_elements):
    """
    Annotates each element in the XML tree with a validation status.
    Adds an `is_valid` attribute with values 'true' or 'false' to each element.
    Adds a `suggest` attribute if there are missing tags for the element.
    
    :param tree: The parsed XML tree (etree.ElementTree).
    :param error_paths: A set of XPath paths indicating elements with validation errors.
    :param missing_elements: Dictionary where keys are paths and values are lists of missing tags.
    """
    for elem in tree.iter():
        # Ensure that the node is an element before adding an attribute
        if isinstance(elem.tag, str):  # This check ensures it's an element, not a comment or text
            # Get the XPath path for the current element
            element_path = tree.getpath(elem)
            
            # Check if this element has an error
            if element_path in error_paths:
                # Add an attribute indicating validation error
                elem.set("is_valid", "false")
            else:
                # Add an attribute indicating validation success
                elem.set("is_valid", "true")
            suggestions = []
                
            # Check if there are missing tags for this element
            if element_path in missing_elements:
                # Join the missing tags with commas to suggest addition
                suggested_tags = ', '.join(missing_elements[element_path])
                suggestions.append(f"Add missing tags: {suggested_tags}")
            if element_path in missing_attributes:
                # Join the missing attributes with commas to suggest addition
                suggested_attributes = ', '.join(missing_attributes[element_path])
                suggestions.append(f"Add missing attributes: {suggested_attributes}")
            if element_path in not_allowed_attributes:
                # Join the not allowed attributes with commas to suggest removal
                not_allowed_attributes = ', '.join(not_allowed_attributes[element_path])
                suggestions.append(f"Remove not allowed attributes: {not_allowed_attributes}")
            if element_path in unexpected_elements:
                if len(unexpected_elements[element_path]) == 1:
                    unexpected_tag = unexpected_elements[element_path][0]
                    suggestions.append(f"Remove unexpected tag '{unexpected_tag}'")
                else:
                    unexpected_tag, expected_tags = unexpected_elements[element_path]
                    suggestions.append(f"Replace unexpected tag '{unexpected_tag}' with one of: {', '.join(expected_tags)}")

            if suggestions:
                # Add a 'suggest' attribute with the suggestions
                elem.set("suggest", '; '.join(suggestions))