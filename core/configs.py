import yaml
import logging
import re
import os

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger('afterchive')

def _read_yaml(file_path):
    logger.info(f"Loading configuration from {file_path}")
    
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
            logger.debug(f"Config data: {config}")
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {file_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML file: {e}")
        raise

    return config


def _substitute_env_vars(obj):
    """Replace ${VAR_NAME} with environment variable values"""
    if isinstance(obj, dict):
        return {k: _substitute_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # Find ${VAR_NAME} patterns
        matches = re.findall(r'\$\{([^}]+)\}', obj)
        for var in matches:
            value = os.getenv(var)
            if not value:
                raise ValueError(f"Environment variable ${{{var}}} not set")
            obj = obj.replace(f'${{{var}}}', value)
    return obj


def parse_yaml_config(file_path, command):
    config_dict = _read_yaml(file_path)


    config_dict = config_dict.get(command, {})

    config_dict = _substitute_env_vars(config_dict)
    
    db_config = {key:value for key, value in config_dict.get("database").items()} 

    storage_config = {key:value for key, value in config_dict.get("storage").items()}

    clean_config = {
        "storage": [storage_config], 
        "databases": [db_config]
    }

    return clean_config