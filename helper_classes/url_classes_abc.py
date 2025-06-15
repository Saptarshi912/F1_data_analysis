from abc import ABC, abstractmethod
import httpx
class URLBase(ABC):
   
    def __init__(self, url,template_url=None,year_dependent=False,race_dependent=False,current_race=0,current_year=0):
        if year_dependent and race_dependent:
            self.url = template_url.format(year=current_year,race_round=current_race)
        elif year_dependent and not race_dependent:
            self.url = template_url.format(year=current_year)
        elif race_dependent and not year_dependent:
            self.url = template_url.format(race_round=current_race)
        else:
            self.url = url
    
    @abstractmethod
    def get_data(self):
        with httpx.Client() as client:
            resp_msg=""
            response = client.get(self.url)
            if response.status_code == 200:
                data = response.json() 
                resp_msg="Success"
            else:
                data = None
                resp_msg="Failed"
            return {"data":data,"resp_msg":resp_msg}

