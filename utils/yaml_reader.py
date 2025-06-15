import os
import yaml

def load_yaml_file(file_path):
    """
    Load and parse a YAML file.
    
    Args:
        file_path (str): Path to the YAML file
        
    Returns:
        dict: Parsed YAML data
    """
    try:
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return None


