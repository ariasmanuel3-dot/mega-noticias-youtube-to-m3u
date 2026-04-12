from pathlib import Path
from playwright.sync_api import sync_playwright

PAGE_URL = "https://www.meganoticias.cl/senal-en-vivo/meganoticias/"
OUTPUT = Path("out/mega.m3u")
OUTPUT.parent.mkdir(exist_ok=True)

def choose_best(candidates: list[str]) -> str:
    for url in candidates:
        if "master.m3u8" in url.lower():
            return url
    for url in candidates:
        lower = url.lower()
        if "playlist" in lower or "index" in lower:
            return url
    return candidates[0]

def main() -> None:
    found: list[str] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        def on_response(response):
            url = response.url
            if ".m3u8" in url and url not in found:
                found.append(url)
                print("FOUND:", url)

        page.on("response", on_response)
        page.goto(PAGE_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(15000)
        browser.close()

    if not found:
        raise RuntimeError("No m3u8 captured from runtime network requests")

    stream_url = choose_best(found)

    content = (
        '#EXTM3U\n'
        '#EXTINF:-1 tvg-id="mega.noticias" tvg-name="Mega Noticias" '
        'group-title="Chile",Mega Noticias\n'
        f'{stream_url}\n'
    )

    OUTPUT.write_text(content, encoding="utf-8")
    print("WRITTEN:", OUTPUT)
    print("USING:", stream_url)

if __name__ == "__main__":
    main()
