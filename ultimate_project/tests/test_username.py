from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter
import time

# USERS
LOGIN_REG = "user2"
PASSWORD = "password"

SENTENCE = "Je suis "
BASE_URL = "https://localhost:8443"

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True
    )
    page = context.new_page()

    def login():
        expect(page).to_have_url(f"{BASE_URL}/login/")

        # Fill in the username and password
        page.locator("#username").fill(LOGIN_REG)
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

    def test_view(locator):
        page.goto(f"{BASE_URL}/login/")

        login()

        page.locator(f"#{locator}").click()

        # Extract username
        username = page.locator("#player").text_content().removeprefix("Je suis ")

        # Assertion on the first try
        assert username == LOGIN_REG

        page.reload()
        assert username == LOGIN_REG
        
        time.sleep(1)
        
        page.reload()
        assert username == LOGIN_REG

        logout()

    # ! =============== KICKSTART TESTER HERE ===============

    test_view("nav-match")
    test_view("nav-tournoi")

    print(f"✅ USERNAME PASSED INTO MATCH / TOURNAMENT ✅")

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
