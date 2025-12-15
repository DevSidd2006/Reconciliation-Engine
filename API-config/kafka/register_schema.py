import requests
import json

# Load schema file
with open("schemas/transaction.avsc", "r") as f:
    schema_str = f.read()

# Schema Registry requires schema as a string
payload = {
    "schema": schema_str
}

headers = {
    "Content-Type": "application/vnd.schemaregistry.v1+json"
}

# Send to Schema Registry
response = requests.post(
    "http://localhost:8081/subjects/transactions-value/versions",
    headers=headers,
    data=json.dumps(payload)
)

print("Status:", response.status_code)
print("Response:", response.text)
