from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter

# USERS
LOGIN_REG = "same_auth"
LOGIN_2FA = "same_auth_2fa"
PASSWORD = "password"
SECRET_2FA = "9JUF2KESUQR45MRTL7MXDSJVI6JQDG42"

SIMULTANEOUS_USERS = 2


BASE_URL = "https://localhost:8443"

def run(playwright: Playwright) -> None:
    # browser = playwright.chromium.launch(headless=False)
    # context = browser.new_context(
    #     ignore_https_errors=True
    # )
    # page = context.new_page()

    def login(page):
        pass

    def logout(page):
        youpiBanane = page.locator("#youpiBanane")
        logoutButton = page.locator("#logoutButton")
        modalLogoutButton = page.locator("#modalLogoutButton")
        assert "show" not in (youpiBanane.get_attribute("class") or "")
        youpiBanane.click()
        logoutButton.click()
        modalLogoutButton.click()
        expect(page).to_have_url(f"{BASE_URL}/login/")

    def init_win(browsers, contexts, pages):
        for _ in range(SIMULTANEOUS_USERS):
            browsers.append(playwright.chromium.launch(headless=False))
            # browsers[_] = playwright.chromium.launch(headless=False)
            # contexts[_] = browsers[_].new_context(ignore_https_errors=True)
            contexts.append(browsers[_].new_context(ignore_https_errors=True))
            pages.append(contexts[_].new_page())

    def destroy_obj(browsers, contexts):
        for context in contexts:
            context.close()
        for browser in browsers:
            browser.close()

        # for _ in range(SIMULTANEOUS_USERS):
        #     contexts[_].close()
    
    def test_reg_users(browsers, contexts, pages):

        init_win(browsers, contexts, pages)
        
        
        destroy_obj(browsers, contexts)
        pass
    
    def test_2fa_users():
        pass
    # ! =============== KICKSTART TESTER HERE ===============
    browsers = []
    contexts = []
    pages = []
    
    test_reg_users(browsers, contexts, pages)

    test_2fa_users()

    print(f"✅ SAMETIME AUTH PASSED ✅")

    # context.close()
    # browser.close()


with sync_playwright() as playwright:
    run(playwright)
