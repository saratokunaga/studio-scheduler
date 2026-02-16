from playwright.sync_api import sync_playwright
import json
import sys

def main():
    url = "https://reserva.be/studio_yomoda/reserve?mode=service_staff&search_evt_no=40eJwzNDAyNrIAAAQZATE"

    print("[BOOT] starting...", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        def handle_response(resp):
            # 例外が起きても必ずログに出す
            try:
                u = resp.url
                if "AjaxSearch" in u:
                    print("\n[FOUND] AjaxSearch:", u, flush=True)
                    ct = resp.headers.get("content-type", "")
                    print("[INFO] content-type:", ct, flush=True)

                    # まず本文を少しだけ見る（Cloudflare HTMLを判定するのに有効）
                    text = resp.text()
                    head = text[:300].replace("\n", "\\n")
                    print("[BODY_HEAD]", head, flush=True)

                    # JSONなら整形表示
                    try:
                        data = resp.json()
                        print("[JSON_KEYS]", list(data.keys())[:30], flush=True)
                        print("[JSON_SNIP]", json.dumps(data, ensure_ascii=False)[:800], flush=True)
                    except Exception as e:
                        print("[NOT_JSON] json parse failed:", repr(e), flush=True)

            except Exception as e:
                print("[HANDLER_ERROR]", repr(e), flush=True)

        # 監視を最初に仕込む
        page.on("response", handle_response)

        print("[NAV] goto", url, flush=True)
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # クリックできるかチェック（失敗ならここで理由が出る）
        try:
            page.locator("text=02/18").first.wait_for(timeout=5000)
            print("[CLICK] clicking 02/18", flush=True)
            page.click("text=02/18")
        except Exception as e:
            print("[CLICK_FAIL]", repr(e), flush=True)

        print("[WAIT] 10s for network...", flush=True)
        page.wait_for_timeout(10000)

        print("[DONE] closing browser", flush=True)
        browser.close()

if __name__ == "__main__":
    # 標準出力バッファ対策
    sys.stdout.reconfigure(line_buffering=True)
    main()
