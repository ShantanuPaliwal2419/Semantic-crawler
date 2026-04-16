


from bs4 import BeautifulSoup
from fastapi import requests
from pydantic.dataclasses import dataclass


@dataclass
class ExtractedPage:
    url : str
    title: str
    description: str
    text : str
    headings : list[str]
    metadata : dict
def extract_metadata(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # TITLE 
    title = (
        (soup.find("title").get_text(strip=True) if soup.find("title") else "")
        or (soup.find("meta", property="og:title").get("content", "") if soup.find("meta", property="og:title") else "")
        or (soup.find("h1").get_text(strip=True) if soup.find("h1") else "")
        or ""
    )

    #  DESCRIPTION 
    description = (
        (soup.find("meta", attrs={"name": "description"}).get("content", "") if soup.find("meta", attrs={"name": "description"}) else "")
        or (soup.find("meta", property="og:description").get("content", "") if soup.find("meta", property="og:description") else "")
        or (soup.find("meta", attrs={"name": "twitter:description"}).get("content", "") if soup.find("meta", attrs={"name": "twitter:description"}) else "")
        or (soup.find("p").get_text(strip=True) if soup.find("p") else "")
        or ""
    )

    #  KEYWORDS 
    keywords = (
        (soup.find("meta", attrs={"name": "keywords"}).get("content", "") if soup.find("meta", attrs={"name": "keywords"}) else "")
        or ""
    )

    return {
        "title": title,
        "description": description,
        "keywords": keywords

    }
def extract_headings(soup: BeautifulSoup) -> list[str]:
    headings = []

    for tag in ["h1", "h2", "h3"]:
        for heading in soup.find_all(tag):
            text = heading.get_text(strip=True)
            if text:
                headings.append(text)

    return headings  
def extract(url:str, html:str) -> ExtractedPage:
    extract_metadata(html)