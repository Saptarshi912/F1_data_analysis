import os
from pathlib import Path
from typing import Dict, Any
from helper_classes.url_factory import create_handlers_from_yaml
from utils.yaml_reader import load_yaml_file

class F1DataPipeline:
    def __init__(self, config_path: str = None, config_file: str = None):
        """
        Initialize the F1 data pipeline.
        
        Args:
            config_path: Path to the config directory
            config_file: Name of the YAML config file
        """
        self.project_root = str(Path(__file__).parent)
        self.config_path = config_path or os.path.join(self.project_root, 'config')
        self.config_file = config_file or 'race_config.yaml'
        self.handlers = {}
        self.data = {}
        
    def initialize(self):
        """Initialize the pipeline by loading configuration and creating handlers"""
        try:
            # Load configuration
            config = load_yaml_file(os.path.join(self.config_path, self.config_file))
            if not config:
                raise ValueError("Failed to load configuration")
                
            # Create handlers
            self.handlers = create_handlers_from_yaml(self.config_path, self.config_file)
            print(f"Initialized pipeline with {len(self.handlers)} endpoints")
            return True
            
        except Exception as e:
            print(f"Failed to initialize pipeline: {str(e)}")
            return False
    
    def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch data from all configured endpoints"""
        if not self.handlers:
            if not self.initialize():
                return {}
                
        for name, handler in self.handlers.items():
            try:
                print(f"Fetching data for {name}...")
                response = handler.get_data()
                if response.resp_msg == "Success":
                    self.data[name] = response.data
                    print(f"Successfully fetched {name} data")
                else:
                    print(f"Failed to fetch {name}: {response.resp_msg}")
            except Exception as e:
                print(f"Error fetching {name}: {str(e)}")
                
        return self.data
    
    def get_handler(self, endpoint_name: str):
        """Get a specific handler by name"""
        return self.handlers.get(endpoint_name)
    
    def get_data(self, endpoint_name: str):
        """Get data from a specific endpoint"""
        if endpoint_name in self.data:
            return self.data[endpoint_name]
        return None

# Example usage
if __name__ == "__main__":
    # Initialize the pipeline
    pipeline = F1DataPipeline()
    
    # Option 1: Fetch all data
    all_data = pipeline.fetch_all_data()
    
    # Option 2: Get a specific handler and fetch data
    race_handler = pipeline.get_handler('race')
    if race_handler:
        race_data = race_handler.get_data()
        print(f"Race data: {race_data}")