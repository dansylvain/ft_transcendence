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
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    # Added timeouts
    page.set_default_timeout(20000) # 20 seconds timeout for Playright
    page.set_default_navigation_timeout(20000) # # 20 seconds timeout for browser

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

        # Wait for the content to be available
        page.wait_for_selector("#players", state="attached")

        # Extract username from self-player and assert it matches LOGIN_REG
        self_player_username = (
            page.locator("#players .self-player").text_content().strip()
        )
        # print(f"✅ Self player username: {self_player_username}")

        # Simple assertion to verify username matches
        assert (
            self_player_username == LOGIN_REG
        ), f"Username mismatch: found '{self_player_username}', expected '{LOGIN_REG}'"

        # Verify username persists after page reload
        page.reload()
        page.wait_for_selector("#players", state="attached")
        time.sleep(0.5)  # Brief wait for content to load

        reload_username = page.locator("#players .self-player").text_content().strip()
        assert (
            reload_username == LOGIN_REG
        ), f"Username mismatch after reload: found '{reload_username}', expected '{LOGIN_REG}'"

        logout()

    # ! =============== KICKSTART TESTER HERE ===============

    test_view("nav-match")
    test_view("nav-tournoi")

    print(f"✅ USERNAME PASSED INTO MATCH / TOURNAMENT ✅")

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
