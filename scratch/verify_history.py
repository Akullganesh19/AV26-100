from playwright.sync_api import sync_playwright
import time

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the local preview using filepath
        page.goto("http://localhost:4173/login")
        time.sleep(3)
        page.screenshot(path="/home/jules/verification/login_screen.png")

        browser.close()

if __name__ == "__main__":
    run_verification()
