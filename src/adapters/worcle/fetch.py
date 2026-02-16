import requests

def fetch_html(url: str) -> str:
    print("Fetching:", url)

    res = requests.get(url)
    res.raise_for_status()  # エラー検知

    return res.text
