import os
import json
from azure.storage.blob import BlobServiceClient

# Load config
with open("config/config.json", "r") as file:
    config = json.load(file)

AZURE_STORAGE_CONNECTION_STRING = config["AZURE_STORAGE_CONNECTION_STRING"]
CONTAINER_NAME = config["CONTAINER_NAME"]

def list_blobs():
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        print(f"Listing blobs in container: {CONTAINER_NAME}")
        blob_names = [blob.name for blob in container_client.list_blobs()]
        return blob_names
    except Exception as e:
        print(f"Error: {e}")
        return []

def list_local_files():
    try:
        parent_directory = os.path.dirname(os.path.abspath(__file__))
        local_files = [f for f in os.listdir(parent_directory) if os.path.isfile(os.path.join(parent_directory, f))]
        return local_files
    except Exception as e:
        print(f"Error: {e}")
        return []


def compare_files():
    blobs = list_blobs()
    local_files = list_local_files()
    missing_files = [file for file in local_files if file not in blobs]
    return missing_files

def upload_files(files):
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        parent_directory = os.path.dirname(os.path.abspath(__file__))
        
        for file in files:
            file_path = os.path.join(parent_directory, file)
            blob_client = container_client.get_blob_client(file)
            
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"Uploaded: {file}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    missing_files = compare_files()
    print("Local files not found in Azure Blob Storage:", missing_files)
    if missing_files:
        upload_files(missing_files)

