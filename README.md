# Enhanced XML Validation Tool
This project enhances the XML validation capabilities of the [xmlschema library](https://github.com/sissaschool/xmlschema) by enabling continuous validation of entire XML files. Instead of stopping at the first encountered error, this tool processes all validation issues, logs them, and provides annotated XML output indicating validation issues and suggested corrections.

## Quickstart:

> Required Python 3.8+!
1. `git clone https://github.com/MaorLavi/XMLInsight.git`
2. `cd XMLInsight`
3. `pip install xmlschema==3.4.2 lxml==5.3.0`
4. Run from the `validating_xml_files.py` file

## Usage:

* `schema_path`: Path to the XML Schema Definition (XSD) file.
* `source_xml`: Path to the XML file to be validated.
* `errors_output`: Path to the log file for validation errors.
* `mod_output_xml`: Path to the annotated XML output file.

## Suggested Data to Test this Project On

The `tests/examples` folder includes XML files and XSD schemas sourced from the `xmlschema` library. Some XML files have been modified to introduce validation errors, with filenames indicating these errors. These files provide effective test cases to demonstrate the tool's error logging and annotation capabilities.

### Specific Data Suggestions

- **Vehicles Dataset**:  
  Use `XMLInsight/tests/examples/vehicles/vehicles.xsd` with `XMLInsight/tests/examples/vehicles/vehicles_errors.xml`. This combination will trigger various validation errors, including unexpected and missing elements and attributes.

- **Collection Dataset**:  
  Use `tests/examples/collection/collection.xsd` with `tests/examples/collection/collection-1_error.xml`. This will produce several errors related to data type mismatches.