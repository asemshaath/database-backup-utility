from google.cloud import storage
from .base import StorageStrategy
import os
from google.api_core.exceptions import GoogleAPIError, NotFound, Forbidden
from google.auth.credentials import AnonymousCredentials
import traceback
import tempfile
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('afterchive')

class GoogleCloudStorage(StorageStrategy):

    def store(self, backup_path, config):
        try:

            if config.get('credentials'):
                cred_path = config.get('credentials')
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Credentials file not found at {cred_path}")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

            # Initialize GCS client
            # client = storage.Client(project=config.get('project'))
            client = self._get_client(config)
            bucket_name = config.get('bucket')
            path = config.get('path', '')  # ← Default to empty string, not None
            
            bucket = client.bucket(bucket_name)

            filename = os.path.basename(backup_path)
            
            # Cleaner path construction
            if path:
                full_gcs_path = f"{path.strip('/')}/{filename}"
            else:
                full_gcs_path = filename

            blob = bucket.blob(full_gcs_path)

            blob.upload_from_filename(backup_path)
            logger.info(f"Backup uploaded to gs://{bucket_name}/{full_gcs_path}")
            
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
        except PermissionError as e:
            logger.error(f"Authentication or permission error: {e}")
        except Forbidden as e:
            logger.error(f"Permission denied when accessing bucket '{config.get('bucket')}': {e}")
            raise ValueError(f"GCS permission denied. Check your credentials and bucket permissions.")
        except NotFound as e:
            logger.error(f"Bucket or path not found: {e}")
            raise ValueError(f"GCS bucket '{config.get('bucket')}' does not exist.")

        except ValueError as e:
            logger.error(f"Configuration error: {e}")
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
        except GoogleAPIError as e:
            logger.error(f"Google API error: {e.message}")
            raise ValueError(f"Failed to upload to GCS: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while storing backup: {str(e)}")
            traceback.print_exc()
            raise e
    
    def retrieve(self, backup_name, config):
        try:
            
            if config.get('credentials'):
                cred_path = config.get('credentials')
                if not os.path.exists(cred_path):
                    raise FileNotFoundError(f"Credentials file not found at {cred_path}")
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path

            storage_client = client = self._get_client(config)
            bucket = storage_client.bucket(config.get('bucket'))
            full_gcs_path = (
                f"{config.get('path')}/{backup_name}"
                if config.get('path') not in (None, '')
                else backup_name
            )

            blob = bucket.blob(full_gcs_path)
            temp_dir = tempfile.mkdtemp()
            destination_file_name = os.path.join(temp_dir, backup_name)
            blob.download_to_filename(destination_file_name)
            logger.info(f"Backup '{backup_name}' downloaded to temporary location: {destination_file_name}")
            return destination_file_name
        except FileNotFoundError as e:
            logger.error(f"File not found error: {e}")
            raise e
        except PermissionError as e:
            logger.error(f"Authentication or permission error: {e}")
            raise e
        except Forbidden as e:
            logger.error(f"Permission denied when accessing bucket '{config.get('bucket')}': {e}")
            raise ValueError(f"GCS permission denied. Check your credentials and bucket permissions.")
        except NotFound as e:
            logger.error(f"Bucket or path not found: {e}")
            raise ValueError(f"GCS bucket '{config.get('bucket')}' does not exist.")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise e
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise e
        except GoogleAPIError as e:
            logger.error(f"Google API error: {e.message}")
            raise ValueError(f"Failed to upload to GCS: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while storing backup: {str(e)}")
            traceback.print_exc()
            raise e

    def _get_client(self, config):
        emulator_host = os.getenv("STORAGE_EMULATOR_HOST")
        if emulator_host:
            logger.info(f"Using GCS emulator at {emulator_host}")
            client = storage.Client(
                credentials=AnonymousCredentials(),
                project="test-project-id",
                client_options={"api_endpoint": emulator_host}
            )
        else:
            # Use default authentication for production
            client = storage.Client(project=config.get('project'))
        return client
