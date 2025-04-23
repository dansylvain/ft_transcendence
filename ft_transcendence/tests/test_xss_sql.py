from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter
import time

LOGIN = "user2"
PASSWORD = "password"
BASE_URL = "https://localhost:8443"

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True
    )
    page = context.new_page()

    # Added timeouts
    page.set_default_timeout(20000) # 20 seconds timeout for Playright
    page.set_default_navigation_timeout(20000) # # 20 seconds timeout for browser

    def login(username):
        page.locator("#username").fill(username)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()

    # def logout():
    #     youpiBanane = page.locator("#youpiBanane")
    #     logoutButton = page.locator("#logoutButton")
    #     modalLogoutButton = page.locator("#modalLogoutButton")
    #     assert "show" not in (youpiBanane.get_attribute("class") or "")
    #     youpiBanane.click()
    #     logoutButton.click()
    #     modalLogoutButton.click()
    #     expect(page).to_have_url(f"{BASE_URL}/login/")

    # ! =============== KICKSTART TESTER HERE ===============
    
    page.goto(f"{BASE_URL}/login/")

    SQL = {
        "username: ' OR '1'='1",
        "admin' --",
        "' UNION SELECT null, 'hacked', null --",
        "' OR IF(1=1, SLEEP(5), 0) --",
    }

    XSS = {
        "<script>alert('XSS')</script>",
        "<p>You searched for: <script>alert('XSS')</script></p>",
        "<a href=\"javascript:alert('XSS')\">Click me</a>",
        "<div onclick=\"alert('XSS')\">Click here</div>",
        "<input value=\"<?php echo $_GET['name']; ?>\">",
        "\" onfocus=\"alert('XSS')",
    }

    # TEST SQL / XSS on login page
    for sql in SQL:
        login(sql)
        time.sleep(0.5)
        error_message = page.locator("#login-form")
        expect(error_message).to_have_text("Invalid credentials")
        
    for xss in XSS:
        login(xss)
        time.sleep(0.5)
        error_message = page.locator("#login-form")
        expect(error_message).to_have_text("Invalid credentials")
    
    # TEST SQL / XSS on register page

    # Login within the website
    time.sleep(1)
    login(LOGIN)
    time.sleep(2)
    expect(page).to_have_url(f"{BASE_URL}/home/")


    # TEST SQL / XSS on the SETUP 2FA
    page.goto(f"{BASE_URL}/account/security/setup-2fa/")

    # ! NOTE : A pure digit form can't accept those two lists, fails at every call
    for sql in SQL:
        try:
            twofa_input = page.locator("#otp_input").fill(sql)
            time.sleep(0.5)
        except Exception as e:
            pass
    for xss in XSS:
        try:
            twofa_input = page.locator("#otp_input").fill(xss)
            time.sleep(0.5)
        except Exception as e:
            pass

    # TEST SQL / XSS on the DELETE ACCOUNT
    page.goto(f"{BASE_URL}/account/confidentiality/delete-account/")

    for sql in SQL:
        # print(f"CURRENT SQL TESTED = {sql}")
        page.locator("#password").fill(sql)
        page.locator("#delete-acc-btn").click()
        time.sleep(0.2)
        error_message = page.locator("#error-input-delete-acc").text_content().strip()
        assert error_message == "The password you entered is incorrect."

    for xss in XSS:
        # print(f"CURRENT XSS TESTED = {xss}")
        page.locator("#password").fill(xss)
        page.locator("#delete-acc-btn").click()
        time.sleep(0.2)
        error_message = page.locator("#error-input-delete-acc").text_content().strip()
        assert error_message == "The password you entered is incorrect."

    # logout()

    print(f"✅ SQL / XSS PASSED ✅")

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
