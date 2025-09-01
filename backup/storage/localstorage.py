from .base import StorageStrategy
import os
import subprocess
import sys

class LocalStorage(StorageStrategy):
    def store(self, backup_path, config):
        # /local/path/
        destination = config.get('path', None)
        try:
            os.makedirs(destination, exist_ok=True)
            dest_file = os.path.join(destination, os.path.basename(backup_path))
            subprocess.run(['cp', backup_path, dest_file], check=True)
            print(f"Backup stored at {dest_file}")
            
        except Exception as e:
            print(f"Failed to store backup: {e}")
            sys.exit(1)

    def retrieve(self, backup_file, config):
        pass