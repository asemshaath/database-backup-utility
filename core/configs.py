import yaml
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('afterchive')

def _read_yaml(file_path):
    logger.info(f"Loading configuration from {file_path}")
    
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        logger.debug(f"Config data: {config}")

    return config

def parse_yaml_config(file_path, command):
    config_dict = _read_yaml(file_path)
    config_dict = config_dict.get(command, {})
    
    db_config = {key:value for key, value in config_dict.get("database").items()} 

    storage_config = {key:value for key, value in config_dict.get("storage").items()}

    print(db_config)
    print(storage_config)

    clean_config = {
        "storage": [storage_config], 
        "databases": [db_config]
    }

    return clean_config