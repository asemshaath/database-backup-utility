from google.cloud import storage
import os
from google.api_core.exceptions import GoogleAPIError, NotFound, Forbidden
import traceback

class GoogleCloudStorage:

    def store(self, backup_path, config):
        try:

            # check required config keys
            missing_keys = [k for k in ['project', 'bucket'] if not config.get(k)]
            if missing_keys:
                raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")

            if config.get('credentials'):
                cred_path = config.get('credentials')
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Credentials file not found at {cred_path}")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

            # Initialize GCS client
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
        except FileNotFoundError as e:
            print(f"File not found error: {e}")
        except Forbidden as e:
            print(f"Permission denied when accessing bucket '{config.get('bucket')}': {e}")
        except NotFound as e:
            print(f"Bucket or path not found: {e}")
        except ValueError as e:
            print(f"Configuration error: {e}")
        except ConnectionError as e:
            print(f"Connection error: {e}")
        except GoogleAPIError as e:
            print(f"Google API error: {e.message}")
        except Exception as e:
            print(f"Unexpected error while storing backup: {str(e)}")
            traceback.print_exc()
            raise e
    
    def retrieve(self, backup_file, config):
        pass