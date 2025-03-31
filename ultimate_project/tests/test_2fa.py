from playwright.sync_api import Playwright, sync_playwright, expect
import time
import pyotp

# test_2fa user secret
LOGIN_SECRET = "S3EF2KESUQR45MRTL7MXDSJVI6JQDG4R"


BASE_URL = "https://localhost:8443"

REGISTER_USERNAME = "register-2fa-test"
LOGIN_USERNAME = "test_2fa"
REGISTER_EMAIL = "register-2fa-test@test.com"
PASSWORD = "password"

# ! =============== TESTING 2FA ===============


def run(playwright: Playwright) -> None:

    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(ignore_https_errors=True)
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

    def get_ordinal_suffix(num):
        if num == 1:
            return "st"
        elif num == 2:
            return "nd"
        elif num == 3:
            return "rd"
        else:
            return "th"

    def test_login_2fa(username, input_secret):
        # Create a TOTP object
        totp = pyotp.TOTP(input_secret)

        page.goto(f"{BASE_URL}/login/")

        # ! ============= LOGIN PAGE =============
        # Fill in the username and password
        expect(page).to_have_url(f"{BASE_URL}/login/")
        page.locator("#username").fill(username)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()

        # ! ============= TWO-FA PAGE =============
        expect(page).to_have_url(f"{BASE_URL}/two-factor-auth/")

        # Fill with a wrong code
        page.locator("#otp_input").fill("000000")
        page.locator("#otp_verify").click()
        expect(page).to_have_url(f"{BASE_URL}/two-factor-auth/")
        error_message = page.locator("#login_error")
        expect(error_message).to_have_text("Invalid 2FA code")

        # Click on the cancel button
        page.locator("#cancel_button").click()

        # ! ============= LOGIN PAGE =============
        expect(page).to_have_url(f"{BASE_URL}/login/")

        # Fill in the username and password
        page.locator("#username").fill(username)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()

        # ! ============= TWO-FA PAGE =============
        expect(page).to_have_url(f"{BASE_URL}/two-factor-auth/")

        # Fill with a correct code
        for _ in range(3):
            current_code = totp.now()
            try:
                page.locator("#otp_input").fill(current_code)
                page.locator("#otp_verify").click()
                expect(page).to_have_url(f"{BASE_URL}/home/")
                print(
                    f"✅ 2FA connexion succed on {_ + 1}{get_ordinal_suffix(_ + 1)} try ✅",
                    flush=True,
                )
                break
            except Exception as e:
                print(f"💀 2FA connexion failed {_ + 1} times, retrying 💀", flush=True)
        
        # logout()

    def test_register_2fa():

        page.goto(f"{BASE_URL}/register/")

        # ! ============= REGISTER PAGE =============
        expect(page).to_have_url(f"{BASE_URL}/register/")

        # Fill in the username and password
        page.locator("#first_name").fill("test")
        page.locator("#last_name").fill("test")
        page.locator("#username").fill(REGISTER_USERNAME)
        page.locator("#email").fill(REGISTER_EMAIL)
        page.locator("#password").fill(PASSWORD)
        page.locator("#repeat_password").fill(PASSWORD)

        page.locator("#register-button").click()

        # ! ============= HOME PAGE =============
        expect(page).to_have_url(f"{BASE_URL}/home/")

        # Go to profile page
        page.locator("#nav-profile").click()

        # ! ============= PROFILE PAGE =============
        expect(page).to_have_url(f"{BASE_URL}/user/profile/")

        # Check is 2FA is not enabled
        expect(page.locator("#disable_2fa")).to_be_hidden()
        expect(page.locator("#setup_2fa")).to_be_visible()

        # Click on setup 2FA
        page.locator("#setup_2fa").click()

        # ! ============= TWO-FA PAGE =============

        EXTRACTED_SECRET = page.locator("#secret_key").text_content()
        print(f"🐛🐛🐛 CURRENT 2FA : {EXTRACTED_SECRET}", flush=True)
        register_totp = pyotp.TOTP(EXTRACTED_SECRET)

        # TRY TO SETUP 2FA
        for _ in range(3):
            try:
                # Wait for the input field to be visible and fill it
                otp_input = page.locator("#otp_input")
                otp_input.fill(register_totp.now())

                # Wait for the verify button to be visible and clickable
                verify_button = page.locator("#otp_verify")
                verify_button.click()

                # Wait for success message to be visible
                success_message = page.locator("#twofa_success_message")
                success_message.wait_for(state="visible", timeout=5000)
                expect(success_message).to_have_text("2FA Action Complete")

                # Wait for log message to be visible
                log_message = page.locator("#log_message")
                log_message.wait_for(state="visible", timeout=5000)
                expect(log_message).to_have_text(
                    "Your account is now protected with two-factor authentication."
                )
                break
            except Exception as e:
                print(f"💀 2FA connexion failed {_ + 1} times, retrying 💀", flush=True)
        
        logout()

        # LOGIN THE CREATED USER WITH 2FA
        test_login_2fa(REGISTER_USERNAME, EXTRACTED_SECRET)

        # ! ============= HOME PAGE =============
        expect(page).to_have_url(f"{BASE_URL}/home/")

        # Go to profile page
        # ! Sometimes, the website is a bit slow, so try-catch 
        for _ in range(5):
            try:
                page.locator("#nav-profile").click()
                expect(page).to_have_url(f"{BASE_URL}/user/profile/")
                
                expect(page.locator("#disable_2fa")).to_be_enabled()
                expect(page.locator("#setup_2fa")).to_be_hidden()
                break
            except Exception as e:
                print(f"💀 Failing to go to profile on {_ + 1} try, retrying 💀", flush=True)

        # ! ============= PROFILE PAGE =============

        # Click on setup 2FA
        page.locator("#disable_2fa").click()

        # ! TEST INCORRECT INPUT
        otp_input = page.locator("#token")
        otp_input.fill("000000")
        verify_button = page.locator("#otp_verify")
        verify_button.click()

        error_message = page.locator("#error")
        expect(error_message).to_have_text("Invalid 2FA code")

        # ! TRY CORRECT INPUT
        for _ in range(2):
            try:
                # Wait for the input field to be visible and fill it
                otp_input = page.locator("#token")
                # otp_input.wait_for(state="visible", timeout=5000)
                otp_input.fill(register_totp.now())

                verify_button.click()

                # Wait for success message to be visible
                success_message = page.locator("#twofa_success_message")
                success_message.wait_for(state="visible", timeout=5000)
                expect(success_message).to_have_text("2FA Action Complete")

                # Wait for log message to be visible
                log_message = page.locator("#log_message")
                log_message.wait_for(state="visible", timeout=5000)
                expect(log_message).to_have_text(
                    "Two-factor authentication has been disabled for your account."
                )
                break
            except Exception as e:
                print(f"💀 2FA connexion failed {_ + 1} times, retrying 💀", flush=True)
        
        logout()


        # ! Login without the 2FA
        page.goto(f"{BASE_URL}/login/")
        expect(page).to_have_url(f"{BASE_URL}/login/")
        page.locator("#username").fill(REGISTER_USERNAME)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()

        expect(page).to_have_url(f"{BASE_URL}/home/")

        # ! DELETE THE USET TO AVOID DUPLICATES

        page.locator("#nav-profile").click()
        expect(page).to_have_url(f"{BASE_URL}/user/profile/")

        page.locator("#delete_profile").click()

        # ! We're on the delete-profile.html HERE

        final_delete_button = page.locator("#delete_profile")
        password_field = page.locator("#password")

        password_field.fill(PASSWORD)
        final_delete_button.click()
        expect(page).to_have_url(f"{BASE_URL}/register/")

        # Last try to login to check if the user has been correctly deleted
        page.goto(f"{BASE_URL}/login/")
        expect(page).to_have_url(f"{BASE_URL}/login/")
        page.locator("#username").fill(REGISTER_USERNAME)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()

        expect(page).to_have_url(f"{BASE_URL}/login/")
        
        error_message = page.locator("#login-form")
        expect(error_message).to_have_text("Invalid credentials")

    # ! =============== KICKSTART TESTER HERE ===============

    test_login_2fa(LOGIN_USERNAME, LOGIN_SECRET)
    logout()

    test_register_2fa()

    context.close()
    browser.close()

    print(f"✅ 2FA register succed ✅", flush=True)


with sync_playwright() as playwright:
    run(playwright)
