import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

HTML_PATH = Path('/Users/hejinyang/社会学读书笔记/wechat_posts/电价市场化改革与市场势力_微信公众号长图版.html')
OUT_PATH = Path('/Users/hejinyang/社会学读书笔记/wechat_posts/电价市场化改革与市场势力_微信公众号长图版.png')


async def main() -> None:
    url = HTML_PATH.resolve().as_uri()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 900, "height": 1200, "device_scale_factor": 2})
        await page.goto(url, wait_until='domcontentloaded')

        await page.wait_for_load_state('networkidle')

        await page.wait_for_function(
            """
            () => {
              const imgs = Array.from(document.images || []);
              return imgs.every(img => img.complete && img.naturalWidth > 0);
            }
            """,
            timeout=20000,
        )

        await page.wait_for_function(
            """
            () => !!(window.MathJax && window.MathJax.typesetPromise)
            """,
            timeout=30000,
        )

        await page.evaluate(
            """
            async () => {
              await window.MathJax.typesetPromise();
            }
            """
        )

        await page.wait_for_function(
            """
            () => document.querySelectorAll('mjx-container, .MathJax').length >= 2
            """,
            timeout=15000,
        )

        await page.wait_for_timeout(1200)

        container = page.locator('.long-image')
        await container.screenshot(path=str(OUT_PATH), type='png')

        await browser.close()

    print(f'Exported: {OUT_PATH}')


if __name__ == '__main__':
    asyncio.run(main())
