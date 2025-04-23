from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter
import time

USERS = {
    "user2",
    "user3",
    "user4",
    "user5",
}
USERNAME = "test"
PASSWORD = "password"
BASE_URL = "https://localhost:8443"

URLS = [
    f"{BASE_URL}/home/",
    f"{BASE_URL}/tournament/",
    f"{BASE_URL}/tournament/simple-match/",
    f"{BASE_URL}/tournament/tournament/",
    f"{BASE_URL}/account/",
]

WRONG_SUB_URL = "lalalala"

AUTH_PATH = [
    "/login/",
    "/register/",
    "/two-factor-auth/",
]

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    # Added timeouts
    page.set_default_timeout(20000)  # 20 seconds timeout for Playright
    page.set_default_navigation_timeout(20000)  # # 20 seconds timeout for browser

    def login():

        page.goto(f"{BASE_URL}/login/")

        # Fill in the username and password
        page.locator("#username").fill(USERNAME)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()

        expect(page).to_have_url(f"{BASE_URL}/home/")

    def logout():
        youpiBanane = page.locator("#youpiBanane")
        logoutButton = page.locator("#logoutButton")
        modalLogoutButton = page.locator("#modalLogoutButton")
        assert "show" not in (youpiBanane.get_attribute("class") or "")
        youpiBanane.click()
        logoutButton.click()
        modalLogoutButton.click()
        expect(page).to_have_url(f"{BASE_URL}/login/")

    # ! =============== KICKSTART TESTER HERE ===============

    # Test that a 404 displays in auth pages
    for paths in AUTH_PATH:
        page.goto(f"{BASE_URL}{paths}{WRONG_SUB_URL}")
        error = page.locator("#error-page").inner_text()
        assert error == "404"

    login()

    # Test that a 404 displays within the website on each container
    for urls in URLS:
        page.goto(f"{urls}{WRONG_SUB_URL}")
        error = page.locator("#error-page").inner_text()
        assert error == "404"

    print(f"✅ 404 TESTS ✅")

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
