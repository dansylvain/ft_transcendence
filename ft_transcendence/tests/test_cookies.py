from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter
import time

USERS = {
    "user2",
    "user3",
    "user4",
    "user5",
}

PASSWORD = "password"
BASE_URL = "https://localhost:8443"

# TEST_COOKIE_DELETE_USER = "coockie-delete"
# TEST_COOKIE_DELETE_PASSWORD = "password"

URLS = [
    f"{BASE_URL}/home/",
    f"{BASE_URL}/account/profile/",
    f"{BASE_URL}/account/game-stats/overview/",
    f"{BASE_URL}/tournament/simple-match/",
    f"{BASE_URL}/tournament/tournament/",
]

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(ignore_https_errors=True)
    page = context.new_page()

    # Added timeouts
    page.set_default_timeout(20000)  # 20 seconds timeout for Playright
    page.set_default_navigation_timeout(20000)  # # 20 seconds timeout for browser

    def login(username, password):

        page.goto(f"{BASE_URL}/login/")

        # expect(page).to_have_url(f"{BASE_URL}/login/")

        # Fill in the username and password
        page.locator("#username").fill(username)
        page.locator("#password").fill(password)
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

    def check_cookie(cur_url, expected_cookies=None):

        page.goto(cur_url)
        cookies = context.cookies(page.url)

        cookie_names = [cookie["name"] for cookie in cookies]
        counts = Counter(cookie_names)


        # Expected cookies == NONE => All cokies must be present
        if not expected_cookies:
            expected_cookies = {"access_token", "refresh_token", "csrftoken"}
        elif expected_cookies == 2: #! Deleted access_token to trigger `jwt_refresh_middleware`
            expected_cookies = {"refresh_token", "csrftoken"}
        else:
            # After logout, we have none of the three cookies
            expected_cookies = {}
        
        # print(f"Coockies present = {cookie_names}")

        # Assertions to check if the cookies are correct
        assert all(
            cookie in counts and counts[cookie] == 1 for cookie in expected_cookies
        ), "Duplicate or missing cookies found"

    # ! =============== KICKSTART TESTER HERE ===============

    
    # Test 1: No cookies deleted
    for user in USERS:
        login(user, PASSWORD)

        # Check cookies on all pages
        for url in URLS:
            check_cookie(url)

        logout()

        # Check cookies after logout
        check_cookie(page.url, 1)

        # Test 2: Delete CSRF token during navigation
        login(user, PASSWORD)

        page.goto(f"{BASE_URL}/account/profile/")

        # Delete CSRF token from context
        context.clear_cookies(name="csrftoken")

        page.goto(f"{BASE_URL}/account/profile/")

        check_cookie(page.url, 1)

        expect(page).to_have_url(f"{BASE_URL}/register/")

        # Test 3: Delete access token during navigation
        login(user, PASSWORD)

        page.goto(f"{BASE_URL}/account/profile/")

        # Delete access token from context
        # ! NOTE : Deleting the access token triggers the `jwt_refresh_middleware`, so a new `access_token` is delivered 
        context.clear_cookies(name="access_token")

        page.goto(f"{BASE_URL}/account/profile/")

        check_cookie(page.url, 2)

        expect(page).to_have_url(f"{BASE_URL}/account/profile/")

        logout()
    


    page.goto(f"{BASE_URL}/register/")
    # ! Test 4 : Create an user and delete it
    page.locator("#first_name").fill("haha")
    page.locator("#last_name").fill("hehe")
    page.locator("#username").fill("coockie-delete")
    page.locator("#email").fill("coockies@gamil.com")
    page.locator("#password").fill("password")
    page.locator("#repeat_password").fill("password")
    page.locator("#register-button").click()

    expect(page).to_have_url(f"{BASE_URL}/home/")

    page.goto(f"{BASE_URL}/account/confidentiality/delete-account/")

    page.locator("#delete-acc-btn").click()

    page.locator("#password").fill("password")

    page.locator("#delete-acc-btn").click()

    time.sleep(4)

    check_cookie(page.url, 1)
    
    expect(page).to_have_url(f"{BASE_URL}/register/")

    print(f"✅ COOKIES CREATION / DELETION TESTS PASSED ✅")

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
