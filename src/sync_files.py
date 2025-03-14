import os
import json
import logging
import glob
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient

# Configure logging with datetime-based filenames
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, f"blob_sync_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logging.basicConfig(filename=log_file, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to clean up logs older than 30 days
def cleanup_old_logs():
    cutoff_date = datetime.now() - timedelta(days=30)
    for log in glob.glob(os.path.join(log_directory, "blob_sync_*.log")):
        log_time_str = log.split("blob_sync_")[-1].split(".log")[0]
        try:
            log_time = datetime.strptime(log_time_str, "%Y-%m-%d_%H-%M-%S")
            if log_time < cutoff_date:
                os.remove(log)
                logging.info(f"Deleted old log file: {log}")
        except ValueError:
            pass  # Skip files that don't match expected format

with open("config/config.json", "r") as file:
    config = json.load(file)

# Pull setup from config.json
AZURE_BLOB_SAS_URL = config["AZURE_BLOB_SAS_URL"]
CONTAINER_NAME = config["CONTAINER_NAME"]
src_dir = config["SRC_DIR"]


def list_blobs():
    try:
        logging.info("Listing blobs from Azure Blob Storage")
        blob_service_client = BlobServiceClient(account_url=AZURE_BLOB_SAS_URL)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        blob_names = [blob.name for blob in container_client.list_blobs()]
        logging.info(f"Retrieved {len(blob_names)} blobs from container")
        return blob_names
    except Exception as e:
        logging.error(f"Error listing blobs: {e}")
        return []

def list_local_files():
    try:
        logging.info("Listing local files in project directory")
        local_files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
        logging.info(f"Found {len(local_files)} local files")
        return local_files
    except Exception as e:
        logging.error(f"Error listing local files: {e}")
        return []

def compare_files():
    logging.info("Comparing local files with Azure Blob Storage")
    blobs = list_blobs()
    local_files = list_local_files()
    missing_files = [file for file in local_files if file not in blobs]
    logging.info(f"Found {len(missing_files)} files missing from Azure Blob Storage")
    return missing_files

def upload_files(files):
    try:
        logging.info("Uploading missing files to Azure Blob Storage")
        blob_service_client = BlobServiceClient(account_url=AZURE_BLOB_SAS_URL)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        for file in files:
            file_path = os.path.join(src_dir, file)
            blob_client = container_client.get_blob_client(file)
            
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
    except Exception as e:
        logging.error(f"Error uploading files: {e}")

if __name__ == "__main__":
    logging.info("Starting Azure Blob Storage sync process")
    cleanup_old_logs()
    missing_files = compare_files()
    if missing_files:
        # upload_files(missing_files) # commented out for testing
        for fn in missing_files:
            print(fn)
        logging.info("File upload process completed")
    else:
        logging.info("No missing files found. No uploads needed")
    logging.info("Sync process finished")
