from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter

TEST_LOGIN = "test"
TEST_PASSWORD = "password"
BASE_URL = "https://localhost:8443"

URLS = [ 
        f"{BASE_URL}/home/", 
        f"{BASE_URL}/user/profile/", 
        f"{BASE_URL}/user/stats/",
        f"{BASE_URL}/tournament/simple-match/",
        f"{BASE_URL}/tournament/tournament/"
        ] 

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True
    )
    page = context.new_page()

    def logout():
        youpiBanane = page.locator("#youpiBanane")
        logoutButton = page.locator("#logoutButton")
        modalLogoutButton = page.locator("#modalLogoutButton")
        assert "show" not in (youpiBanane.get_attribute("class") or "")
        youpiBanane.click()
        logoutButton.click()
        modalLogoutButton.click()
        expect(page).to_have_url(f"{BASE_URL}/login/")

    def check_cookie(cur_url, logout = None):

        page.goto(cur_url)
        cookies = context.cookies(page.url)

        cookie_names = [cookie['name'] for cookie in cookies]
        counts = Counter(cookie_names)

        # Expected cookies
        if not logout:
            expected_cookies = {'access_token', 'refresh_token', 'csrftoken'}
        else:
            # After logout, we have only one csrftoken left
            expected_cookies = {'csrftoken'}

        # Assertions
        assert all(counts[cookie] == 1 for cookie in expected_cookies), "Duplicate or missing cookies found"

    # ! =============== KICKSTART TESTER HERE ===============
    
    page.goto(f"{BASE_URL}/login/")

    # LOGIN
    page.locator("#username").fill(TEST_LOGIN)
    page.locator("#password").fill(TEST_PASSWORD)
    page.locator("#loginButton").click()

    expect(page).to_have_url(f"{BASE_URL}/home/")

    for url in URLS:
        check_cookie(url)
    
    logout()

    # Check cookies after logout
    check_cookie(page.url, 1)

    print(f"✅ COOKIES TESTS PASSED ✅")

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
