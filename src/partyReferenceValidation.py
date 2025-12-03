import json
from jsonschema import validate, Draft7Validator, exceptions

# Load schema from external file
with open("partyReferenceSchema.json", "r", encoding="utf-8") as f:
    party_schema = json.load(f)

# Load JSON data to validate from external file
with open("partyReference.json", "r", encoding="utf-8") as f:
    party_data = json.load(f)

# Validate JSON against schema
try:
    validate(instance=party_data, schema=party_schema)
    print("JSON is valid against schema ✅")
except exceptions.ValidationError as e:
    print("JSON validation error ❌:", e.message)

# Optional: collect all errors
validator = Draft7Validator(party_schema)
errors = sorted(validator.iter_errors(party_data), key=lambda e: e.path)
for error in errors:
    print("Error at", list(error.path), ":", error.message)
