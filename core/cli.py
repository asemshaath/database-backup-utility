import argparse
from databases import get_strategy
from storage import get_storage_strategy
import os
import sys

def main():
    """
    This is the main function that contains the primary logic of the script.

    # Example usage:
    # db-backup backup --db-type postgres --db mydb
        db-backup backup \
        --db-type postgres \
        --host localhost --db mydb --user admin \
        --cloud s3 \
        --bucket my-db-backups \
        --path prod/postgres \
        --region us-east-1
    """

    # Call other functions or perform operations here
    parser = argparse.ArgumentParser(
                    prog='afterchive',
                    description='Database Backup Utility',
                    epilog='')
    
    # Create parent parser with common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument('--config', help='Path to config file')
    parent_parser.add_argument('--db-host', help='Database host')
    parent_parser.add_argument('--db-user', help='Database username') 
    parent_parser.add_argument('--db-pass', help='Database password (or set DB_PASSWORD env var)')
    parent_parser.add_argument('--db-name', help='Database name')
    parent_parser.add_argument('--db-type', help='Type of the database (e.g., postgres, mysql)')
    parent_parser.add_argument('--db-port', type=int, help='Database port number')
    parent_parser.add_argument('--storage', help='Cloud provider (e.g., s3, gcs, or local for local filesystem)')
    parent_parser.add_argument('--bucket', help='Cloud storage bucket name')
    parent_parser.add_argument('--path', help='Path in the cloud storage bucket')
    parent_parser.add_argument('--region', help='Cloud storage region (if applicable)')
    parent_parser.add_argument('--credentials', help='Path to cloud provider credentials file')
    parent_parser.add_argument('--project', help='Project ID for Google Cloud Storage (optional)')
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Create subparsers that inherit from parent
    backup_parser = subparsers.add_parser('backup', parents=[parent_parser], help='Backup a database')
    restore_parser = subparsers.add_parser('restore', parents=[parent_parser], help='Restore a database')
    
    # Add restore-specific argument
    restore_parser.add_argument('--backup-file', help='Path to the backup file for restoration')

    args = parser.parse_args()

    # Support environment variables for sensitive data
    db_password = args.db_pass or os.getenv('AFTERCHIVE_DB_PASSWORD')
    args.db_pass = db_password

    if args.command in ['backup', 'restore']:
        # Quick check for critical fields
        if not all([args.db_type, args.db_host, args.db_name, args.storage]):
            print("Error: Missing required arguments (db-type, db-host, db-name, storage)")
            parser.print_help()
            sys.exit(1)

    if args.command == 'backup':
        print(f"Backing up database {args.db_name} of type {args.db_type} to {args.storage} at path {args.path}")
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