from google.cloud import storage
import os

class GoogleCloudStorage:

    def store(self, backup_path, config):
        try:
            if config.get('credentials'):
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.get('credentials')

            client = storage.Client(project=config.get('project'))
            bucket_name = config.get('bucket')
            path = config.get('path')
            
            

            bucket = client.bucket(bucket_name)

            full_gcs_path = (
                f"{path}/{backup_path.split('/')[-1]}"
                if path not in (None, '')
                else backup_path.split('/')[-1]
            )

            blob = bucket.blob(full_gcs_path)

            blob.upload_from_filename(backup_path)
            print(f"Backup {backup_path} uploaded to {full_gcs_path} in bucket {bucket_name}.")
        except Exception as e:
            print(f"Failed to store backup: {e}")
            raise e
    
    def retrieve(self, backup_file, config):
        pass