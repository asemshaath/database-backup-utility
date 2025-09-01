from .localstorage import LocalStorage

STRATEGIES = {
    "local": LocalStorage,
    # "mysql": MySQLBackup,
}

def get_storage_strategy(storage_type: str):
    try:
        return STRATEGIES[storage_type]
    except KeyError:
        raise ValueError(f"Unsupported storage type: {storage_type}")
