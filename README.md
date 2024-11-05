# Enhanced XML Validation Tool
This project enhances the XML validation capabilities of the [xmlschema library](https://github.com/sissaschool/xmlschema) by enabling continuous validation of entire XML files. Instead of stopping at the first encountered error, this tool processes all validation issues, logs them, and provides annotated XML output indicating validation issues and suggested corrections.

## Quickstart:

> Required Python 3.8+!
1. `git clone `
2. `cd `
3. `pip install xmlschema==3.4.2 lxml==5.3.0`
4. Run from the `validating_xml_files.py` file

## Usage:

* `schema_path`: Path to the XML Schema Definition (XSD) file.
* `source_xml`: Path to the XML file to be validated.
* `errors_output`: Path to the log file for validation errors.
* `mod_output_xml`: Path to the annotated XML output file.

## Suggested Data to test this project on:

In the `tests/examples` folder includes XML files and XSD schemas sourced from the xmlschema library. Some of the XML files have been modified to introduce validation errors, with filenames indicating the presence of these errors.