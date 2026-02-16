import asyncio
from playwright.async_api import async_playwright

STUDIOS = {
    "A館 - Studio.A1（57㎡）":
        "40eJwzNDAyNrIAAAQZATE",
    "A館 - Studio.A2（74㎡）":
        "77eJwzNDAyNjYCAAQVASw",
    "A館 - Studio.A3（74㎡）":
        "35eJwzNDAyNjYGAAQWAS0",
    "B館 - Studio.B2":
        "47eJwzNDAyNjYDAAQZATA",
    "B館 - Studio.B3":
        "56eJwzNDAyNjYHAAQaATE",
    "B館 - Studio.B4":
        "5ceJwzNDAyNrYAAAQbATI",
    "B館 - Studio.B5":
        "65eJwzNDAyNrYEAAQcATM",
}


async def fetch_one_async(browser, name, evt):

    print(f"[OPEN] {name}")

    context = await browser.new_context()

    page = await context.new_page()

    url = (
        "https://reserva.be/studio_yomoda/reserve"
        f"?mode=service_staff&search_evt_no={evt}"
    )

    await page.goto(url)

    # calendarロード待ち
    await page.wait_for_selector("text=02/17", timeout=20000)

    # AjaxSearchを待機しながらクリック
    async with page.expect_response(
        lambda r: "AjaxSearch" in r.url,
        timeout=20000
    ) as resp:

        await page.click("text=02/17")

    response = await resp.value

    data = await response.json()

    await context.close()

    return data


def fetch_all(headless=True):

    async def runner():

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=headless
            )

            results = {}

            for name, evt in STUDIOS.items():

                results[name] = await fetch_one_async(
                    browser,
                    name,
                    evt
                )

            await browser.close()

            return results

    return asyncio.run(runner())
