from .localstorage import LocalStorage
from .gcp import GoogleCloudStorage

STRATEGIES = {
    "local": LocalStorage,
    "google": GoogleCloudStorage,
    "gcs": GoogleCloudStorage,
    "gcp": GoogleCloudStorage,
}

def get_storage_strategy(storage_type: str):
    try:
        return STRATEGIES[storage_type]()
    except KeyError:
        raise ValueError(f"Unsupported storage type: {storage_type}")
