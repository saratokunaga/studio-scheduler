from playwright.sync_api import sync_playwright
import json

url = "https://reserva.be/studio_yomoda/reserve?mode=service_staff&search_evt_no=40eJwzNDAyNrIAAAQZATE"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 最初はFalse推奨
    context = browser.new_context()
    page = context.new_page()

    page.goto(url)

    # Cloudflare突破待ち
    page.wait_for_timeout(5000)

    # AjaxSearchのレスポンスを捕まえる
    def handle_response(response):
        if "AjaxSearch" in response.url:
            print("FOUND AjaxSearch:", response.url)
            try:
                data = response.json()
                print(json.dumps(data, indent=2)[:1000])
            except:
                print("Not JSON")

    page.on("response", handle_response)

    # 日付クリックなどをトリガー
    page.click("text=02/18")

    page.wait_for_timeout(5000)

    browser.close()
