from  datetime import datetime
import urllib.robotparser
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from pydantic.dataclasses import dataclass
@dataclass
class RawPage :
    url: str
    html: str
    status_code : int
    fetched_at:datetime
@dataclass    
class Page :
    url : str
    html:str
    links : list[str]
    fetched_at:datetime    

def is_allowed_by_robots_txt(url:str) -> bool:
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(url + "/robots.txt")
    try:

       rp.read()
    except:
        return True   
   
    return rp.can_fetch("*", url)
   
def extract_links(html:str, base_url:str) -> list[str]:

    soup = BeautifulSoup(html, "html.parser")
    links = []
    for link in soup.find_all("a", href=True):
      full_url = urljoin(base_url, link["href"])
      if full_url.startswith(("http://", "https://")):
        print(full_url)
        links.append(full_url)
    return list(set(links))
