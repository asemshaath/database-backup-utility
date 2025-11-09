from .base import StorageStrategy
import os
import subprocess
import sys
import tempfile
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('afterchive')

class LocalStorage(StorageStrategy):
    def store(self, backup_path, config):
        # /local/path/
        destination = config.get('path', None)
        try:
            os.makedirs(destination, exist_ok=True)
            dest_file = os.path.join(destination, os.path.basename(backup_path))
            subprocess.run(['cp', backup_path, dest_file], check=True)
            logger.info(f"Backup stored at {dest_file}")
            
        except Exception as e:
            logger.info(f"Failed to store backup: {e}")
            sys.exit(1)

    def retrieve(self, backup_name, config):
        directory = config.get('path', None)
        backup_path = os.path.join(directory, os.path.basename(backup_name))

        if os.path.exists(backup_path):
            logger.info(f"'{backup_name}' exists.")
            temp_dir = tempfile.mkdtemp()

            subprocess.run(['cp', backup_path, temp_dir], check=True)
            temp_backup_path = os.path.join(temp_dir, os.path.basename(backup_name))
            logger.info(f"Backup copied to temporary location: {temp_backup_path}")
            return temp_backup_path
        else:
            raise FileNotFoundError(f"Backup file '{backup_name}' does not exist.")

        