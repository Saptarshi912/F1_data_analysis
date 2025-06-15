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

def extract_endpoints(folder,filename):
    """
    We are extracting the static and year dependent endpoints from the YAML file.
    
    Returns:
        dict: Parsed YAML data
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #yaml_file = os.path.join(base_dir, 'config', 'race_config.yaml')
    yaml_file = os.path.join(base_dir, folder, filename)
    config_data = load_yaml_file(yaml_file)
    
    if not config_data:
        return None
    
    static_endpoints = config_data.get('static_endpoints', {})
    
    year_dependent_endpoints = config_data.get('year_dependent_endpoints', {})
    
    return static_endpoints, year_dependent_endpoints


def normalise_url_schema(conf_dict:dict) -> list:
    """
    We are normalising the URL schema for the endpoints.
    
    Returns:
        dict: Normalised URL schema
    """
    return_list = [{}]*len(conf_dict)
    for index,(key, value) in enumerate(conf_dict.items()):
        return_dict = {"name":key}
        for key,value in value.items():
            return_dict[key] = value
        return_list[index] = return_dict    
    return return_list

def main():
    static_endpoints, year_dependent_endpoints = extract_endpoints('config','race_config.yaml')
    final_list = normalise_url_schema(static_endpoints) + normalise_url_schema(year_dependent_endpoints)
    return final_list
    
if __name__ == "__main__":
    final_list = main()
    print(final_list)
