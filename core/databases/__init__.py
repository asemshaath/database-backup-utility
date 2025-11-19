# from .postgres import PostgresBackup

# STRATEGIES = {
#     "postgres": PostgresBackup,
#     # "mysql": MySQLBackup,
# }

# def get_strategy(db_type: str):
#     try:
#         return STRATEGIES[db_type]()
#     except KeyError:
#         raise ValueError(f"Unsupported DB type: {db_type}")

def get_strategy(db_type: str):
    """Get database strategy with lazy imports"""
    
    if db_type == "postgres":
        try:
            from .postgres import PostgresBackup
            return PostgresBackup()
        except ImportError:
            raise ImportError(
                "PostgreSQL support not installed. "
                "Install with: pip install afterchive[postgres]"
            )
    
    # elif db_type == "mysql":
    #     try:
    #         from .mysql import MySQLBackup
    #         return MySQLBackup()
    #     except ImportError:
    #         raise ImportError(
    #             "MySQL support not installed. "
    #             "Install with: pip install afterchive[mysql]"
    #         )
    
    else:
        raise ValueError(f"Unsupported database type: {db_type}")