import json
import requests
from datetime import datetime
import os

url = "https://admin.karthikacollections.in/v1/graphql"
headers = {
    "Content-Type": "application/json",
    "x-hasura-admin-secret": "myadminsecretkey"
}

query = """
query MyQuery {
  mst_category {
    category
    id
    image
    isdeleted
    description
    created_at
  }
}
"""

def fetch_data_from_hasura():
    """Fetches the data from the GraphQL endpoint."""
    response = requests.post(
        url,
        json={"query": query},
        headers=headers,
        verify=False
    )
    if response.status_code == 200:
        return response.json()['data']['mst_category']
    else:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

def save_data_to_json(data, filename):
    """Saves the fetched data to a JSON file."""
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data successfully saved to {filename}")

def load_existing_data(filename):
    """Loads existing data from the JSON file, returns an empty list if the file does not exist or is empty."""
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    else:
        return []

def is_new_record(record, existing_data):
    """Checks if a record is new based on the created_at timestamp."""
    existing_timestamps = [item['created_at'] for item in existing_data]
    record_timestamp = datetime.strptime(record['created_at'], '%Y-%m-%dT%H:%M:%S.%f')
    for timestamp in existing_timestamps:
        existing_timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f')
        # Return False if the record's timestamp is older or equal to an existing record
        if record_timestamp <= existing_timestamp:
            return False
    return True

def update_json_file(filename='/Users/ksuryadodi/Development/python automation/updatefile/mst_category.json'):
    """Fetches new data from Hasura and updates the JSON file with new records."""
    existing_data = load_existing_data(filename)
    new_data = fetch_data_from_hasura()

    # If the file is empty or non-existent, it will be populated with all fetched data
    if not existing_data:
        save_data_to_json(new_data, filename)
    else:
        # Filter for new records based on the created_at timestamp
        new_records = [record for record in new_data if is_new_record(record, existing_data)]
        if new_records:
            # Combine existing data with new records and save
            updated_data = existing_data + new_records
            save_data_to_json(updated_data, filename)
        else:
            print("No new records to add.")

# Call the function to update the JSON file
update_json_file()
