from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, HttpUrl, Field, validator
import httpx


class APIResponse(BaseModel):
    """Pydantic model for API response data structure"""
    data: Optional[Dict[str, Any]]
    resp_msg: str = Field(..., description="Response status message")
    
    @validator('resp_msg')
    def validate_resp_msg(cls, v):
        if v not in ["Success", "Failed"]:
            raise ValueError("resp_msg must be either 'Success' or 'Failed'")
        return v
    
    class Config:
        extra = 'forbid'  # Forbid extra fields
        frozen = True  # Make the model immutable


class URLConfig(BaseModel):
    """Pydantic model for URL configuration"""
    url: Optional[HttpUrl] = None
    template_url: Optional[str] = None
    year_dependent: bool = False
    race_dependent: bool = False
    current_race: int = Field(0, ge=0, le=30)  # Assuming max 30 races in a season
    current_year: int = Field(..., ge=1950, le=2100)  # F1 started in 1950
    
    @validator('template_url', always=True)
    def validate_template_url(cls, v, values):
        if values.get('year_dependent') or values.get('race_dependent'):
            if not v:
                raise ValueError("template_url is required when year_dependent or race_dependent is True")
        return v


class URLBase(ABC):
    """Base class for URL handling with Pydantic validation"""
    
    def __init__(self, url: Optional[str] = None, template_url: Optional[str] = None,
                 year_dependent: bool = False, race_dependent: bool = False,
                 current_race: int = 0, current_year: int = 2023):
        # Validate inputs using Pydantic model
        self.config = URLConfig(
            url=url,
            template_url=template_url,
            year_dependent=year_dependent,
            race_dependent=race_dependent,
            current_race=current_race,
            current_year=current_year
        )
        
        # Build the final URL based on configuration
        self._build_url()
    
    def _build_url(self) -> None:
        """Build the final URL based on configuration"""
        if self.config.year_dependent and self.config.race_dependent:
            self.url = self.config.template_url.format(
                year=self.config.current_year,
                race_round=self.config.current_race
            )
        elif self.config.year_dependent:
            self.url = self.config.template_url.format(
                year=self.config.current_year
            )
        elif self.config.race_dependent:
            self.url = self.config.template_url.format(
                race_round=self.config.current_race
            )
        else:
            if not self.config.url:
                raise ValueError("url is required when not using template_url")
            self.url = self.config.url
    
    @abstractmethod
    def get_data(self) -> APIResponse:
        pass


class StaticURL(URLBase):
    """Class for handling static URLs that don't change based on year or race"""
    
    def __init__(self, url: str):
        if not url:
            raise ValueError("URL cannot be empty for StaticURL")
        super().__init__(url=url, year_dependent=False, race_dependent=False)
    
    def get_data(self) -> APIResponse:
        """Implementation of abstract method from URLBase"""
        with httpx.Client() as client:
            try:
                response = client.get(self.url)
                if response.status_code == 200:
                    return APIResponse(
                        data=response.json(),
                        resp_msg="Success"
                    )
                return APIResponse(
                    data=None,
                    resp_msg=f"Failed with status code: {response.status_code}"
                )
            except Exception as e:
                return APIResponse(
                    data=None,
                    resp_msg=f"Error: {str(e)}"
                )

class YearDependentURL(URLBase):
    """Class for handling URLs that depend on the year"""
    
    def __init__(self, template_url: str, current_year: int,year_dependent: bool = True, **kwargs):
        """
        Initialize a year-dependent URL
        
        Args:
            template_url: URL template containing {year} placeholder
            current_year: The year to use in the URL
            **kwargs: Additional arguments to pass to URLBase
        """
        if not template_url or "{year}" not in template_url:
            raise ValueError("template_url is required and must contain {year} placeholder")
            
        super().__init__(
            template_url=template_url,
            year_dependent=year_dependent,
            race_dependent=False,
            current_year=current_year,
            **kwargs
        )
    
    def get_data(self) -> APIResponse:
        """Implementation of abstract method from URLBase"""
        with httpx.Client() as client:
            try:
                response = client.get(self.url)
                if response.status_code == 200:
                    return APIResponse(
                        data=response.json(),
                        resp_msg="Success"
                    )
                return APIResponse(
                    data=None,
                    resp_msg=f"Failed with status code: {response.status_code}"
                )
            except Exception as e:
                return APIResponse(
                    data=None,
                    resp_msg=f"Error: {str(e)}"
                )
        
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'YearDependentURL':
        """Create a YearDependentURL from a configuration dictionary"""
        return cls(**config)


class RaceDependentURL(URLBase):
    """Class for handling URLs that depend on the race"""
    
    def __init__(self, template_url: str, current_year: int,current_race: int, **kwargs):
        """
        Initialize a race-dependent URL
        
        Args:
            template_url: URL template containing {race_round} placeholder
            current_year: The year to use in the URL
            current_race: The race number to use in the URL
            **kwargs: Additional arguments to pass to URLBase
        """
        if not template_url or "{race_round}" not in template_url:
            raise ValueError("template_url is required and must contain {race_round} placeholder")
            
        super().__init__(
            template_url=template_url,
            year_dependent=True,
            race_dependent=True,
            current_year=current_year,
            current_race=current_race,
            **kwargs
        )
    
    def get_data(self) -> APIResponse:
        """Implementation of abstract method from URLBase"""
        with httpx.Client() as client:
            try:
                response = client.get(self.url)
                if response.status_code == 200:
                    return APIResponse(
                        data=response.json(),
                        resp_msg="Success"
                    )
                return APIResponse(
                    data=None,
                    resp_msg=f"Failed with status code: {response.status_code}"
                )
            except Exception as e:
                return APIResponse(
                    data=None,
                    resp_msg=f"Error: {str(e)}"
                )
        
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> 'RaceDependentURL':
        """Create a RaceDependentURL from a configuration dictionary"""
        return cls(**config)

## STATIC URLS ###
class F1_status_url(StaticURL):
    """Class for handling static URLs that don't change based on year or race"""
    def __init__(self,url):
        super().__init__(url)

class F1_season_url(StaticURL):
    """Class for handling static URLs that don't change based on year or race"""
    def __init__(self,url):
        super().__init__(url)

class F1_circuit_url(StaticURL):
    """Class for handling static URLs that don't change based on year or race"""
    def __init__(self,url):
        super().__init__(url)

################### YEAR DEPENDENT URL ###################
class F1_race_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)

class F1_constructor_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)

class F1_driver_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)

class F1_result_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)  

class F1_sprint_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)

class F1_qualify_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)

class F1_standings_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)

class F1_constructorstanding_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)

class F1_driverstanding_url(YearDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,year_dependent,current_year):
        super().__init__(template_url,year_dependent,current_year)

################### RACE DEPENDENT URL ##################

class F1_pitstop_url(RaceDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,race_dependent,current_year,current_race):
        super().__init__(template_url,race_dependent,current_year,current_race)

class F1_lap_url(RaceDependentURL):
    """Class for handling URLs that depend on the year"""
    def __init__(self,template_url,race_dependent,current_year,current_race):
        super().__init__(template_url,race_dependent,current_year,current_race)