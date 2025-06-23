from typing import Dict, Any, List, Union
from .url_classes_abc import (
    F1_status_url, F1_season_url, F1_circuit_url,
    F1_race_url, F1_constructor_url, F1_driver_url, F1_result_url,
    F1_sprint_url, F1_qualify_url, F1_standings_url,
    F1_constructorstanding_url, F1_driverstanding_url,
    F1_pitstop_url, F1_lap_url
)

class URLFactory:
    """Factory class to create URL handler instances from YAML configuration"""
    
    # Map endpoint names to their corresponding classes
    STATIC_ENDPOINTS = {
        'status': F1_status_url,
        'season': F1_season_url,
        'circuit': F1_circuit_url,
    }
    
    YEAR_DEPENDENT_ENDPOINTS = {
        'race': F1_race_url,
        'constructor': F1_constructor_url,
        'driver': F1_driver_url,
        'result': F1_result_url,
        'sprint': F1_sprint_url,
        'qualify': F1_qualify_url,
        'standings': F1_standings_url,
        'constructorstanding': F1_constructorstanding_url,
        'driverstanding': F1_driverstanding_url,
    }
    
    RACE_DEPENDENT_ENDPOINTS = {
        'pitstop': F1_pitstop_url,
        'lap': F1_lap_url,
    }
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create URL handler instances from configuration
        
        Args:
            config: Dictionary containing endpoint configurations
            
        Returns:
            Dict containing instantiated URL handlers
        """
        handlers = {}
        
        # Process static endpoints
        for name, endpoint_config in config.get('static_endpoints', {}).items():
            if name in cls.STATIC_ENDPOINTS:
                handlers[name] = cls.STATIC_ENDPOINTS[name](url=endpoint_config['url'])
        
        # Process year-dependent endpoints
        for name, endpoint_config in config.get('year_dependent_endpoints', {}).items():
            if name in cls.YEAR_DEPENDENT_ENDPOINTS and endpoint_config.get('year_dependent'):
                handlers[name] = cls.YEAR_DEPENDENT_ENDPOINTS[name](
                    template_url=endpoint_config['template_url'],
                    year_dependent=endpoint_config.get('year_dependent', True),
                    current_year=endpoint_config.get('current_year', 2023)
                )
        
        # Process race-dependent endpoints
        for name, endpoint_config in config.get('race_specific_endpoints', {}).items():
            if name in cls.RACE_DEPENDENT_ENDPOINTS and endpoint_config.get('race_dependent'):
                handlers[name] = cls.RACE_DEPENDENT_ENDPOINTS[name](
                    template_url=endpoint_config['template_url'],
                    race_dependent=True,
                    current_year=endpoint_config.get('current_year', 2023),
                    current_race=endpoint_config.get('current_race', 1)
                )
        
        return handlers
    
    @classmethod
    def get_handler(cls, config: Dict[str, Any], handler_name: str) -> Any:
        """
        Get a specific handler by name
        
        Args:
            config: Configuration dictionary
            handler_name: Name of the handler to get
            
        Returns:
            The requested handler instance or None if not found
        """
        handlers = cls.from_config(config)
        return handlers.get(handler_name)


def create_handlers_from_yaml(yaml_path: str, yaml_file: str) -> Dict[str, Any]:
    """
    Create URL handlers from YAML configuration file
    
    Args:
        yaml_path: Path to the YAML file
        yaml_file: Name of the YAML file
        
    Returns:
        Dictionary of URL handlers
    """
    from utils.yaml_reader import load_yaml_file
    import os
    
    # Load YAML config
    config_path = os.path.join(yaml_path, yaml_file)
    config = load_yaml_file(config_path)
    
    if not config:
        raise ValueError(f"Failed to load configuration from {config_path}")
    
    # Create handlers
    return URLFactory.from_config(config)
