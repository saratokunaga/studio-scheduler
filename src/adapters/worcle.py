import json
import requests
from bs4 import BeautifulSoup

def fetch_mydata(url: str) -> dict:
    print("Fetching:", url)

    res = requests.get(url)
    html = res.text

    soup = BeautifulSoup(html, "html.parser")
    
    script_tag = soup.find("script", id = "mydata")

    if not script_tag:
        raise Exception("mydata not found")
    
    data = json.loads(script_tag.text)

    return data