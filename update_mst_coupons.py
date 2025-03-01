import json
import requests
from datetime import datetime
import os

# GraphQL endpoint
url = "https://admin.karthikacollections.in/v1/graphql"
headers = {
    "Content-Type": "application/json",
    "x-hasura-admin-secret": "myadminsecretkey"
}


query = """
query GetMstCoupons {
  mst_coupons {
    isdeleted
		is_public
		min_order_value
		category_id
		customer_id
		product_id
		discount_value
		code
		description
		discount_type
		status
		end_date
		start_date
		updated_at
		created_at
		id
		shop_id
  }
}
    
"""

def fetch_data_from_hasura():
    """Fetches the latest data from the GraphQL API."""
    response = requests.post(url, json={"query": query}, headers=headers, verify=False)
    if response.status_code == 200:
        return response.json().get('data', {}).get('mst_coupons', [])
    else:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

def save_data_to_json(data, filename):
    """Saves the updated data to a JSON file."""
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
    print(f"Data successfully saved to {filename}")

def load_existing_data(filename):
    """Loads existing data from the JSON file."""
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    else:
        return []

def update_json_file(filename='mst_coupons.json'):
    """Updates the JSON file based on created_at and updated_at timestamps."""
    
    existing_data = load_existing_data(filename)
    new_data = fetch_data_from_hasura()

    # Convert existing data into a dictionary {id: record}
    existing_data_map = {item['id']: item for item in existing_data}
    updated_data = []

    for record in new_data:
        record_id = record['id']
        
        if record_id in existing_data_map:
            # Check if the record needs updating based on updated_at
            existing_record = existing_data_map[record_id]
            existing_updated_at = datetime.strptime(existing_record['updated_at'], '%Y-%m-%dT%H:%M:%S.%f') if existing_record.get('updated_at') else None
            new_updated_at = datetime.strptime(record['updated_at'], '%Y-%m-%dT%H:%M:%S.%f') if record.get('updated_at') else None

            if new_updated_at and (not existing_updated_at or new_updated_at > existing_updated_at):
                print(f"Updating record ID {record_id} (updated_at changed).")
                updated_data.append(record)  # Update record
            else:
                updated_data.append(existing_record)  # Keep existing record
        else:
            print(f"Adding new record ID {record_id} (new created_at).")
            updated_data.append(record)  # Add new record

    # Save the updated JSON file
    save_data_to_json(updated_data, filename)

# Run the update function
update_json_file()
