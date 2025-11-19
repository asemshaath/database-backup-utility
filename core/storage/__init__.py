# from .localstorage import LocalStorage
# from .gcp import GoogleCloudStorage

# STRATEGIES = {
#     "local": LocalStorage,
#     "google": GoogleCloudStorage,
#     "gcs": GoogleCloudStorage,
#     "gcp": GoogleCloudStorage,
# }

# def get_storage_strategy(storage_type: str):
#     try:
#         return STRATEGIES[storage_type]()
#     except KeyError:
#         raise ValueError(f"Unsupported storage type: {storage_type}")


def get_storage_strategy(storage_type: str):
    """Get storage strategy with lazy imports"""
    
    if storage_type == "local":
        from .localstorage import LocalStorage
        return LocalStorage()
    
    elif storage_type in ["gcs", "google", "gcp"]:
        try:
            from .gcp import GoogleCloudStorage
            return GoogleCloudStorage()
        except ImportError:
            raise ImportError(
                "GCS support not installed. "
                "Install with: pip install afterchive[gcs]"
            )
    
    elif storage_type in ["s3", "aws"]:
        try:
            from .s3 import S3Storage
            return S3Storage()
        except ImportError:
            raise ImportError(
                "S3 support not installed. "
                "Install with: pip install afterchive[s3]"
            )
    
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")