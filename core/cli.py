import argparse
from databases import get_strategy
from storage import get_storage_strategy
import os
import sys

def main():
    """
    This is the main function that contains the primary logic of the script.
    """
    # Call other functions or perform operations here
    parser = argparse.ArgumentParser(
                        prog='db-backup',
                        description='Database Backup Utility',
                        epilog='')
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    # Example usage:
    # db-backup backup --db-type postgres --db mydb
    """"
        db-backup backup \
        --db-type postgres \
        --host localhost --db mydb --user admin \
        --cloud s3 \
        --bucket my-db-backups \
        --path prod/postgres \
        --region us-east-1
    """

    db_parser = subparsers.add_parser('backup', help='Backup a database')
    db_parser = subparsers.add_parser('restore', help='Restore a database')


    
    db_parser.add_argument('--config', help='Path to config file')
    
    db_parser.add_argument('--db-host', help='Database host')
    db_parser.add_argument('--db-user', help='Database username') 
    db_parser.add_argument('--db-pass', help='Database password')
    db_parser.add_argument('--db-name', help='Database name')
    db_parser.add_argument('--db-type', help='Type of the database (e.g., postgres, mysql)')
    db_parser.add_argument('--db-port', type=int, help='Database port number')

    db_parser.add_argument('--storage', help='Cloud provider (e.g., s3, gcs, or local for local filesystem)')
    db_parser.add_argument('--bucket', help='Cloud storage bucket name')
    db_parser.add_argument('--path', help='Path in the cloud storage bucket to store the backup or local path if type is local (e.g., /local/path/)')
    db_parser.add_argument('--region', help='Cloud storage region (if applicable)')
    db_parser.add_argument('--credentials', help='Path to cloud provider credentials file (if applicable)')
    db_parser.add_argument('--project', help='Project ID for Google Cloud Storage (optional)')

    db_parser.add_argument('--backup-file', help='Path to the backup file for restoration (if applicable)')

    args = parser.parse_args()
    print(args.command)

    if args.command == 'backup':
        print(f"Backing up database {args.db_name} of type {args.db_type} to {args.db_type} bucket {args.bucket} at path {args.path}")
        db = get_strategy(args.db_type)
        storage = get_storage_strategy(args.storage)

        db_config = {
            "host": args.db_host,
            "port": args.db_port,
            "dbname": args.db_name,
            "user": args.db_user,
            "password": args.db_pass
        }

        db_file_path = db.backup(config=db_config)

        storage_config = {
            "bucket": args.bucket,
            "path": args.path,
            "region": args.region,
            "type": args.storage,
            "credentials": args.credentials,
            "project": args.project
        }

        storage.store(backup_path=db_file_path, config=storage_config)

        os.remove(db_file_path)
        print(f"Temporary backup file {db_file_path} removed.")
    elif args.command == 'restore':
        # Here you would add the logic to perform the restore
        db = get_strategy(args.db_type)
        storage = get_storage_strategy(args.storage)
        
        storage_config = {
            "bucket": args.bucket,
            "path": args.path,
            "region": args.region,
            "type": args.storage,
            "credentials": args.credentials,
            "project": args.project
        }

        db_backup_path = storage.retrieve(backup_name= args.backup_file, config=storage_config)

        db_config = {
            "host": args.db_host,
            "port": args.db_port,
            "dbname": args.db_name,
            "user": args.db_user,
            "password": args.db_pass
        }

        db.restore(config={**db_config, "backup_file": db_backup_path})



        os.remove(db_backup_path)
        print(f"Temporary backup file {db_backup_path} removed.")

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()