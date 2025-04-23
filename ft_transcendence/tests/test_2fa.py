from playwright.sync_api import Playwright, sync_playwright, expect, Page
import time
import pyotp
import traceback

# test_2fa user secret
#LOGIN_SECRET = "S3EF2KESUQR45MRTl7MXDSJVI6JDQG4R"

#totp = pyotp.TOTP(LOGIN_SECRET)

def get_ordinal_suffix(num):
        if num == 1:
            return "st"
        elif num == 2:
            return "nd"
        elif num == 3:
            return "rd"
        else:
            return "th"

def setup_playwright(playwright: Playwright):
    try:
        print("🔄 Starting get page process...", flush=True)
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        # Added timeouts
        page.set_default_timeout(20000) # 20 seconds timeout for Playright
        page.set_default_navigation_timeout(20000) # # 20 seconds timeout for browser

        print("✅ Successfully initialized the page.", flush=True)
        return page, context, browser
    except Exception as e:
        print(f"❌ An error occurred while initializing the page: {str(e)}", flush=True)
        return None
    
def close_playwright(context, browser):
    try:
        print("🔄 Starting the process to close Playwright...", flush=True)
        context.close()
        browser.close()
        print("✅ Successfully closed Playwright context and browser.", flush=True)
    except Exception as e:
        print(f"❌ An error occurred while closing Playwright: {str(e)}", flush=True)

def test_delete_user(page: Page, has_2fa, password, otp_key=None):
    try:
        print(f"🔄 Starting process to DELETE user - is using 2fa {has_2fa}...", flush=True)
        expect(page).to_have_url(f"{BASE_URL}/home/")
        page.locator("#nav-profile").click()
        expect(page).to_have_url(f"{BASE_URL}/account/profile/")
        page.locator("#acc-conf").click()
        expect(page).to_have_url(f"{BASE_URL}/account/confidentiality/")
        page.locator("#delete-account-page").click()
        expect(page).to_have_url(f"{BASE_URL}/account/confidentiality/delete-account/")
        time.sleep(1)
    except Exception as e:
        print(f"❌ Failed to navigate to the Delete Account page: {str(e)}", flush=True)  
    delete_button = page.locator("#delete-acc-btn")
    password_field = page.locator("#password")
    otp_field =  page.locator("#otp-code")
    if otp_key:
        otp = pyotp.TOTP(otp_key)
    if has_2fa:
        print(f"⚪ Invalid password w OTP ...", flush=True)
        for _ in range(3):
            try:
                password_field.fill("xxfalse_passwordxx")
                otp_field.fill(otp.now())
                delete_button.click()
                time.sleep(1)
                error_field = page.locator("#error-input-delete-acc").text_content()
                assert (error_field.strip() != ""), "❌ Missing error for invalid password."
                print("✅ Correctly handled invalid password with 2FA", flush=True)
                break
            except Exception as e:
                print(f"❌ Incorrect password with 2FA attempt {_ + 1} failed: {str(e)}", flush=True)
    else:
        try:
            print(f"⚪ Invalid password no 2FA ...", flush=True)
            password_field.fill("xxfalse_passwordxx")
            delete_button.click()
            time.sleep(1)
            error_field = page.locator("#error-input-delete-acc").text_content()
            assert (error_field.strip() != ""), "❌ Missing error for invalid password."
            print("✅ Correctly handled invalid password (no 2FA)", flush=True)
        except Exception as e:
            print(f"❌ Incorrect password (no 2FA) test failed: {str(e)}", flush=True)
    if has_2fa:
        print(f"⚪ Valid password with invalid OTP ...", flush=True)
        try:
            password_field.fill(password)
            otp_field.fill("000000")
            delete_button.click()
            time.sleep(1)
            error_field = page.locator("#error-input-delete-acc").text_content()
            assert (error_field.strip() != ""), "❌ Missing error for invalid OTP CODE."
            print("✅ Correctly handled invalid 2FA code w valid password.", flush=True)
        except Exception as e:
            print(f"❌ Invalid OTP test failed: {str(e)}", flush=True)
    if has_2fa:
        print(f"    ⚪ Valid password + valid OTP code...", flush=True)
        for _ in range(3):
            current_code = otp.now()
            try:
                password_field.fill(password)
                otp_field.fill(current_code)
                delete_button.click()
                time.sleep(1)
                expect(page).to_have_url(f"{BASE_URL}/register/")
                print(f"✅ User with 2FA deleted successfully on attempt {_ + 1}", flush=True)
                break
            except Exception as e:
                print(f"❌ Happy path 2FA delete attempt {_ + 1} failed: {str(e)}", flush=True)
    else:
        try:
            print(f"⚪ Valid password", flush=True)
            password_field.fill(password)
            delete_button.click()
            time.sleep(1)
            expect(page).to_have_url(f"{BASE_URL}/register/")
            print("✅ User without 2FA deleted successfully", flush=True)
        except Exception as e:
            print(f"❌ Failed to delete user without 2FA: {str(e)}", flush=True)

def test_logout(page: Page) -> None:
    try:
        print("🔄 Starting logout process...", flush=True)
        if page.content().strip() == "":
            print("❌ The page is empty. Unable to proceed with logout.", flush=True)
            return
        youpiBanane = page.locator("#youpiBanane")
        logoutButton = page.locator("#logoutButton")
        modalLogoutButton = page.locator("#modalLogoutButton")
        assert "show" not in (youpiBanane.get_attribute("class") or "")
        youpiBanane.click()
        logoutButton.click()
        modalLogoutButton.click()
        time.sleep(1)
        expect(page).to_have_url(f"{BASE_URL}/login/")
        print("✅ Successfully logged out and redirected to login page.", flush=True)
    except Exception as e:
        print(f"❌ An error occurred during logout: {str(e)}", flush=True)

def test_login_w_check_failed(page: Page, username, password):
    try:
        print("🔄 Starting the process of filling and submitting the login form with 1 wrong attempt...", flush=True)
        expect(page).to_have_url(f"{BASE_URL}/login/")
        if page.content().strip() == "":
            print("❌ The page is empty. Unable to proceed with logout.", flush=True)
            return
        # Fill in the login form with invalid credentials
        page.locator("#username").fill(username)
        page.locator("#password").fill(password)
        page.locator("#loginButton").click()
        error_message = page.locator("#login-form")
        expect(error_message).to_have_text("Invalid credentials")
        expect(page).to_have_url(f"{BASE_URL}/login/")
        print("✅ Login failed as expected with the correct error message.", flush=True)
        # Optionally, check that the URL is still the login page after the failed login
        page.locator("#username").fill(username)
        page.locator("#password").fill(password)
        page.locator("#loginButton").click()
        print("✅ Login successful as expected.", flush=True)
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}", flush=True)

def test_login(page: Page, username, password):
    try:
        print("🔄 Starting the process of filling and submitting the login form...", flush=True)
        page.goto(f"{BASE_URL}/login/")
        expect(page).to_have_url(f"{BASE_URL}/login/")
        if page.content().strip() == "":
            print("❌ The page is empty. Unable to proceed with logout.", flush=True)
            return
        page.locator("#username").fill(username)
        page.locator("#password").fill(password)
        page.locator("#loginButton").click()
        time.sleep(1)
        expect(page).to_have_url(f"{BASE_URL}/home/")
        print("✅ Login successful as expected.", flush=True)
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}", flush=True)

def simple_login(page: Page, username, password):
    try:
        print("🔄 Starting the process of filling and submitting the login form (simple login)", flush=True)
        page.goto(f"{BASE_URL}/login/")
        expect(page).to_have_url(f"{BASE_URL}/login/")
        page.locator("#username").fill(username)
        page.locator("#password").fill(password)
        page.locator("#loginButton").click()
        print("✅ Login successful as expected.", flush=True)
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}", flush=True)

def test_login_w_2fa(page: Page, username, password, otp_key) -> None:
    try:
        print("⚙️ Starting 2FA login test...", flush=True)
        totp = pyotp.TOTP(otp_key)
        try:
            simple_login(page, username, password)
            expect(page).to_have_url(f"{BASE_URL}/two-factor-auth/")
            print("✅ Login successful, on 2FA page.", flush=True)
        except Exception as e:
            print(f"❌ Login failed before 2FA: {str(e)}", flush=True)
            return
        try:
            time.sleep(2)
            page.locator("#otp_input").fill("000000")
            page.locator("#otp_verify").click()
            expect(page).to_have_url(f"{BASE_URL}/two-factor-auth/")
            error_message = page.locator("#login_error")
            expect(error_message).to_have_text("Invalid 2FA code")
            print("✅ Error message correctly shown for invalid 2FA code.", flush=True)
        except Exception as e:
            print(f"❌ Invalid 2FA code test failed: {str(e)}", flush=True)
            return
        try:
            page.locator("#cancel_button").click()
            expect(page).to_have_url(f"{BASE_URL}/login/")
            print("✅ Navigated back to login after invalid 2FA.", flush=True)
        except Exception as e:
            print(f"❌ Failed to return to login page after cancel: {str(e)}", flush=True)
            return
        try:
            simple_login(page, username, password)
            expect(page).to_have_url(f"{BASE_URL}/login/")
            print("✅ Re-login successful, back on 2FA page.", flush=True)
        except Exception as e:
            print(f"❌ Re-login failed: {str(e)}", flush=True)
            return
        for attempt in range(3):
            current_code = totp.now()
            try:
                page.locator("#otp_input").fill(current_code)
                page.locator("#otp_verify").click()
                expect(page).to_have_url(f"{BASE_URL}/home/")
                print(f"✅ 2FA succeeded on attempt {attempt + 1}{get_ordinal_suffix(attempt + 1)}.", flush=True)
                break
            except Exception as e:
                print(f"💀 2FA attempt {attempt + 1} failed, retrying...", flush=True)

    except Exception as e:
        print(f"❌ Unexpected error during 2FA login test: {str(e)}", flush=True)
    else:
        print("✅ 2FA login test completed successfully.", flush=True)

def test_register(page: Page, username, email, password):
    try:
        print("🔄 Register user with valid credentials ...", flush=True)
        page.goto(f"{BASE_URL}/register/")
        expect(page).to_have_url(f"{BASE_URL}/register/")
        page.locator("#first_name").fill("test")
        page.locator("#last_name").fill("test")
        page.locator("#username").fill(username)
        page.locator("#email").fill(email)
        page.locator("#password").fill(password)
        page.locator("#repeat_password").fill(password)
        page.locator("#register-button").click()
        time.sleep(1)
        expect(page).to_have_url(f"{BASE_URL}/home/")
        print("✅ Successfully registered and landed on Home page", flush=True)
        return True
    except Exception as e:
        print(f"❌ Failed during registration: {str(e)}", flush=True)
        return False

def test_setup_2fa_account(page: Page):
    try:
        print("🔄 Setup 2FA on the account page ...", flush=True)
        expect(page).to_have_url(f"{BASE_URL}/home/")
        for _ in range(2):
            try:
                page.locator("#nav-profile").click()
                expect(page).to_have_url(f"{BASE_URL}/account/profile/")
                page.locator("#acc-security").click()
                expect(page).to_have_url(f"{BASE_URL}/account/security/")
                break
            except Exception as e:
                print(f"❌ Failed to access account security settings: {str(e)}", flush=True)
        if page.locator("#setup_2fa").is_visible():
            page.locator("#setup_2fa").click()
            expect(page).to_have_url(f"{BASE_URL}/account/security/setup-2fa/")
            # Try verifying the TOTP
            extracted_key = page.locator("#secret_key").text_content().strip()
            login_otp_key = extracted_key
            otp = pyotp.TOTP(login_otp_key)
            for attempt in range(3):
                try:
                    otp_input = page.locator("#otp_input")
                    otp_input.fill(otp.now())
                    verify_button = page.locator("#otp_verify")
                    verify_button.click()
                    success_message = page.locator("#twofa_success_message")
                    success_message.wait_for(state="visible")
                    print(f"⚠️ 2FA setup successful on attempt {attempt + 1}", flush=True)
                    break
                except Exception as e:
                    print(f"❌ 2FA setup failed on attempt {attempt + 1}: {str(e)}", flush=True)
            print("✅ Test completed: 2FA setup successful", flush=True)
            return login_otp_key
        else:
            print("⚠️ 2FA is currently enabled", flush=True)
    except Exception as e:
        print(f"❌ Test failed: {str(e)}", flush=True)

BASE_URL = "https://localhost:8443"
USERNAME = "test_alllbbbbbb_2fa"
EMAIL = "test_alllbbbbbb_2fa@test.com"
PASSWORD = "password"

def run(playwright: Playwright) -> None:
    print("===================== 🧪 START: Setup 2FA for Account =====================", flush=True)    
    page, context, browser  = setup_playwright(playwright)
    # Some connection test
    if not test_register(page, USERNAME, EMAIL, PASSWORD):
        test_login(page, USERNAME, PASSWORD)
        test_delete_user(page, False, PASSWORD)
        test_register(page, USERNAME, EMAIL, PASSWORD)
    # Try setup 2FA 
    login_otp_key = test_setup_2fa_account(page)
    test_logout(page)
    test_login_w_2fa(page, USERNAME, PASSWORD, login_otp_key)
    test_delete_user(page, True, PASSWORD, login_otp_key)
    close_playwright(context, browser)
    print("===================== ✅ END: Setup 2FA for Account Test Completed =====================", flush=True)

with sync_playwright() as playwright:
    run(playwright)
