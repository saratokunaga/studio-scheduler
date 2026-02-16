# src/adapters/yomoda/fetch.py

from __future__ import annotations
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright


def fetch_mydata(
    url: str,
    target_date_slash: str,
    reserve_bus_cd: str = "306558",
    reserve_ist_no: str = "102328",
    profile_dir: str = "pw_profile_yomoda",
    headless: bool = True,
) -> Dict[str, Any]:
    """
    worcle と同じ感じで "mydata相当"（= AjaxSearchのJSON）を取って返す
    Cloudflare対策として，Chromeで通った永続プロファイル(profile_dir)を使う

    url: https://reserva.be/studio_yomoda/availability
    target_date_slash: '2026/02/17'
    """

    payload = {
        "cmd": "get_new_institution",
        "reserve_bus_cd": reserve_bus_cd,
        "reserve_ist_no": reserve_ist_no,
        "target_date": target_date_slash,
        "mode": "",
        "first_flg": "1",
        "month_week": "week",
        "datetime_max_days": "1",
        "select_timeorday": "1",
        "price_type_no": "0",
    }

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=headless,
        )
        page = ctx.new_page()

        # ここで "AjaxSearch" のレスポンスJSONを拾う
        captured: Dict[str, Any] = {}

        def handle_response(resp):
            try:
                if "/AjaxSearch" in resp.url and resp.request.method == "POST":
                    ct = resp.headers.get("content-type", "")
                    if "application/json" in ct or "text/javascript" in ct:
                        captured["json"] = resp.json()
            except Exception:
                # CF/一時的エラーなどは握りつぶして次へ
                pass

        page.on("response", handle_response)

        page.goto(url, wait_until="domcontentloaded")

        # in-page fetch で AjaxSearch を叩く（requests直叩きより403になりにくい）
        page.evaluate(
            """
            async (payload) => {
              const r = await fetch("https://reserva.be/AjaxSearch", {
                method: "POST",
                headers: {
                  "accept": "application/json, text/javascript, */*; q=0.01",
                  "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                  "x-requested-with": "XMLHttpRequest",
                },
                body: new URLSearchParams(payload).toString(),
                credentials: "include",
              });
              return { status: r.status, ct: r.headers.get("content-type") || "" };
            }
            """,
            payload,
        )

        # 少し待つ（responseハンドラで拾う）
        page.wait_for_timeout(1500)

        ctx.close()

        if "json" not in captured:
            raise RuntimeError(
                "AjaxSearch JSONを取得できませんでした"
                "Cloudflare/プロファイル未通過の可能性があります"
                "headless=Falseで一度開いて，人間チェック通過後に再実行してください"
            )

        return captured["json"]
