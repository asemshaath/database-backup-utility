from .postgres import PostgresBackup

STRATEGIES = {
    "postgres": PostgresBackup,
    # "mysql": MySQLBackup,
}

def get_strategy(db_type: str):
    try:
        return STRATEGIES[db_type]()
    except KeyError:
        raise ValueError(f"Unsupported DB type: {db_type}")
