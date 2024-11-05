import xmlschema
from enhanced_validation import validate_enhanced

schema_path = 'tests/examples/vehicles/vehicles.xsd'
my_schema = xmlschema.XMLSchema(schema_path)
source_xml = 'tests/examples/vehicles/vehicles_errors.xml'
errors_output = 'errors.log'
mod_output_xml = 'annotated_file.xml'

validate_enhanced(my_schema, source_xml, output_file=errors_output, modified_output_file=mod_output_xml)
