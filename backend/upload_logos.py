from google.cloud import storage
import os

def upload_file(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

bucket_name = "sandbox-426014-a2ui-media-cache"
data_dir = os.path.join(os.path.dirname(__file__), 'data', 'logos')

try:
    upload_file(bucket_name, os.path.join(data_dir, 'workday.png'), 'logos/workday.png')
    upload_file(bucket_name, os.path.join(data_dir, 'aon.png'), 'logos/aon.png')
except Exception as e:
    print(f"Error uploading logos: {e}")
