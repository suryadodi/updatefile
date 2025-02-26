import json
import requests
from datetime import datetime
import os

# Hasura GraphQL API details
url = "https://admin.karthikacollections.in/v1/graphql"
headers = {
    "Content-Type": "application/json",
    "x-hasura-admin-secret": "myadminsecretkey"
}

# Load existing mst_category.json
def load_existing_data(filename="mst_category.json"):
    """Loads existing JSON data."""
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        with open(filename, "r") as f:
            return json.load(f)
    return []

# Get the latest timestamp from existing data
def get_latest_timestamp(existing_data):
    """Finds the most recent updated_at or created_at timestamp from the JSON data."""
    if not existing_data:
        return "2000-01-01T00:00:00"  # Default old date if no data exists
    return max(record.get("updated_at", record["created_at"]) for record in existing_data)

# Fetch updated/new records from Hasura
def fetch_updated_data(last_sync):
    """Fetches only new or updated records from Hasura."""
    query = """
    query MyQuery($last_sync: timestamptz!) {
      mst_category(where: {
        _or: [
          { created_at: { _gt: $last_sync } }
          { updated_at: { _gt: $last_sync } }
        ]
      }) {
        id
        category
        image
        isdeleted
        description
        created_at
        updated_at
      }
    }
    """
    variables = {"last_sync": last_sync}
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json().get("data", {}).get("mst_category", [])
    else:
        raise Exception(f"Failed to fetch data: {response.status_code} - {response.text}")

# Update existing data in-place
def update_existing_data(existing_data, new_data):
    """Updates existing data with new records while replacing updated ones."""
    existing_data_dict = {item["id"]: item for item in existing_data}  # Convert list to dict (id as key)

    for record in new_data:
        existing_data_dict[record["id"]] = record  # Replace if exists or add new

    return list(existing_data_dict.values())  # Convert back to list

# Save updated data to mst_category.json
def save_data_to_json(data, filename="mst_category.json"):
    """Saves updated data to JSON."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data successfully updated in {filename}")

# Main function to update mst_category.json
def update_json_file():
    """Updates mst_category.json with new or updated records."""
    existing_data = load_existing_data()  # Load existing JSON data
    last_sync = get_latest_timestamp(existing_data)  # Get the latest timestamp
    new_data = fetch_updated_data(last_sync)  # Fetch new or updated records

    if new_data:
        updated_data = update_existing_data(existing_data, new_data)  # Update existing records
        save_data_to_json(updated_data)  # Save updated JSON
    else:
        print("No new or updated records found.")

# Run the update process
update_json_file()
