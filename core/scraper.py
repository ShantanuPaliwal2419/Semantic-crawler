from  datetime import datetime
import urllib.robotparser
from cohere import client
import requests
import httpx
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse

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
    status_code: int 
class settings:
    DEFAULT_CRAWL_DELAY_MS = 1000  # 1 second 
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
        
        links.append(full_url)
    return list(set(links))


from datetime import datetime
import httpx

async def fetch_page(url: str) -> RawPage:
    async with httpx.AsyncClient() as client:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
            response = await client.get(url, timeout=10, headers=headers)

            return RawPage(
                url=url,
                html=response.text,
                status_code=response.status_code,
                fetched_at=datetime.now()
            )

        except Exception as e:
            print(f"Error fetching {url}: {e}")

            return RawPage(
                url=url,
                html="",
                status_code=0,
                fetched_at=datetime.now()
            )

async def crawl(url: str , max_pages: int, max_depth: int) -> list[Page]:
    queue = [(url, 0)]
    visited = set()
    results = []
    seed_domain = urlparse(url).netloc
    while queue and len(results) < max_pages:
        url, current_depth = queue.pop(0)
        if url in visited :
            continue
        raw_page = await fetch_page(url)
        if not raw_page.html:
            visited.add(url)
            continue
        links = extract_links(raw_page.html, url)
        filtered_links = []
        for link in links:
            if urlparse(link).netloc == seed_domain:
                filtered_links.append(link)    
        if current_depth < max_depth:
         for link in filtered_links:
           if link not in visited and link not in [q[0] for q in queue]:  # add this check
            queue.append((link, current_depth + 1))

        # mark visited
        visited.add(url)

        # append result
        results.append(Page(
            url=url,
            html=raw_page.html,
            links=filtered_links,
            fetched_at=raw_page.fetched_at,
            status_code=raw_page.status_code
        ))

        # crawl delay
        await asyncio.sleep(settings.DEFAULT_CRAWL_DELAY_MS / 1000)

    return results
