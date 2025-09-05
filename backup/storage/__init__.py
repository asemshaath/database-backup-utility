from .localstorage import LocalStorage
from .gcp import GoogleCloudStorage

STRATEGIES = {
    "local": LocalStorage,
    "google": GoogleCloudStorage,
    # "mysql": MySQLBackup,
}

def get_storage_strategy(storage_type: str):
    try:
        return STRATEGIES[storage_type]()
    except KeyError:
        raise ValueError(f"Unsupported storage type: {storage_type}")
