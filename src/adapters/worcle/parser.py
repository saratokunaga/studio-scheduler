import json
from bs4 import BeautifulSoup

def parse_worcle(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    script_tag = soup.find("script", id="mydata")

    if not script_tag:
        raise Exception("mydata not found")

    data = json.loads(script_tag.text)

    return data
