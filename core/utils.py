

def get_cleaned_conf_cli(args):
    storage_config = {
        "bucket": args.bucket,
        "path": args.path,
        "region": args.region,
        "type": args.storage,
        "credentials": args.credentials,
        "project": args.project
    }

    db_config = {
        "host": args.db_host,
        "port": args.db_port,
        "name": args.db_name,
        "user": args.db_user,
        "password": args.db_pass,
        "type": args.db_type
    }

    clean_config = {
        "storage": [storage_config], 
        "databases": [db_config]
    }

    print(clean_config)

    return clean_config