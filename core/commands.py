import logging
import os
import sys
from storage import get_storage_strategy
from databases import get_strategy

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('afterchive')

def backup_command(db_conf, storage_conf):
    logger.info(f"Backing up database {db_conf.get('name')} of type {db_conf.get("type")} to {storage_conf.get('type')} at path {storage_conf.get('path')}")
    
    try:
        db = get_strategy(db_conf.get('type'))
        storage = get_storage_strategy(storage_conf.get('type'))

        db_config = {
            "host": db_conf.get('host'),
            "port": db_conf.get('port'),
            "dbname": db_conf.get('name'),
            "user": db_conf.get('user'),
            "password": db_conf.get('password')
        }

        db_file_path = db.backup(config=db_config)

        storage.store(backup_path=db_file_path, config=storage_conf)

        os.remove(db_file_path)
        logger.info(f"Temporary backup file {db_file_path} removed.")
        logger.info("Backup process completed successfully.")
    except ValueError as e:
        # User-facing errors (wrong password, missing db, etc)
        logger.error(str(e))
        sys.exit(1)
    except Exception as e:
        # Unexpected errors - show some detail but not full traceback
        logger.error(f"Backup failed: {str(e)}")
        logger.debug("Full error:", exc_info=True)  # Only with --verbose
        sys.exit(1)


def restore_command(db_conf, storage_conf, backup_file):
    # Here you would add the logic to perform the restore
    db = get_strategy(db_conf.get('type'))
    storage = get_storage_strategy(storage_conf.get('type'))
    
    # storage_config = {
    #     "bucket": args.bucket,
    #     "path": args.path,
    #     "region": args.region,
    #     "type": args.storage,
    #     "credentials": args.credentials,
    #     "project": args.project
    # }

    db_backup_path = storage.retrieve(backup_name= backup_file, config=storage_conf)

    db_config = {
        "host": db_conf.get('host'),
        "port": db_conf.get('port'),
        "dbname": db_conf.get('name'),
        "user": db_conf.get('user'),
        "password": db_conf.get('password')
    }

    db.restore(config={**db_config, "backup_file": db_backup_path})

    os.remove(db_backup_path)
    logger.info(f"Temporary backup file {db_backup_path} removed.")
    logger.info("Restore process completed successfully.")