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
    updated_at
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

def update_json_file(filename='mst_category.json'):
    """Fetches new data from Hasura and updates the JSON file based on created_at and updated_at timestamps."""
    existing_data = load_existing_data(filename)
    new_data = fetch_data_from_hasura()

    if not existing_data:
        # Save all data if the file is empty
        save_data_to_json(new_data, filename)
        return

    # Convert existing data into a dictionary for quick lookup by ID
    existing_data_dict = {item['id']: item for item in existing_data}

    updated_records = []
    for record in new_data:
        record_id = record['id']
        record_created_at = datetime.strptime(record['created_at'], '%Y-%m-%dT%H:%M:%S.%f')
        record_updated_at = datetime.strptime(record['updated_at'], '%Y-%m-%dT%H:%M:%S.%f')

        if record_id in existing_data_dict:
            existing_record = existing_data_dict[record_id]
            existing_created_at = datetime.strptime(existing_record['created_at'], '%Y-%m-%dT%H:%M:%S.%f')
            existing_updated_at = datetime.strptime(existing_record['updated_at'], '%Y-%m-%dT%H:%M:%S.%f')

            # Update the record if created_at or updated_at is newer
            if record_created_at > existing_created_at or record_updated_at > existing_updated_at:
                existing_data_dict[record_id] = record
                updated_records.append(record)
        else:
            # New record, add it
            existing_data_dict[record_id] = record
            updated_records.append(record)

    if updated_records:
        # Save the updated dictionary as a list
        save_data_to_json(list(existing_data_dict.values()), filename)
        print(f"Updated {len(updated_records)} records.")
    else:
        print("No updates found.")

# Call the function to update the JSON file
update_json_file()
