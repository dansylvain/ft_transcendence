from playwright.sync_api import Playwright, sync_playwright, expect
import pyotp
import time

LOGIN_REGULAR = "delete_standard"
PASSWORD = "password"

LOGIN_2FA = "delete_2fa"
OPT_KEY = "S3EF2KESUQR45MRTL7MXDSJVI6JQDG42"

BASE_URL = "https://localhost:8443"

totp = pyotp.TOTP(OPT_KEY)

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True
    )
    page = context.new_page()

    def login(user):
        
        if user == "regular":
            page.locator("#username").fill(LOGIN_REGULAR)
            page.locator("#password").fill(PASSWORD)
            page.locator("#loginButton").click()
        else:
            page.locator("#username").fill(LOGIN_2FA)
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

    def delete_user(user):
        login(user)
        
        # Connect to 2fa
        if user == "2fa":
            for _ in range(3):
                try:
                    page.locator("#otp_input").fill(totp.now())
                    page.locator("#otp_verify").click()
                    expect(page).to_have_url(f"{BASE_URL}/home/")
                    break
                except Exception as e:
                    print(f"💀 2FA connexion failed {_ + 1} times, retrying 💀", flush=True)

        expect(page).to_have_url(f"{BASE_URL}/home/")

        page.locator("#nav-profile").click()
        expect(page).to_have_url(f"{BASE_URL}/user/profile/")

        page.locator("#delete_profile").click()

        # ! We're on the delete-profile.html HERE

        final_delete_button = page.locator("#delete_profile")
        password_field = page.locator("#password")

        # ! CASE 1 INCORRECT PASSWORD

        if user == "2fa":
            for _ in range(3):
                try:
                    password_field.fill("nope")
                    otp_field = page.locator("#otp-code")
                    otp_field.fill(totp.now())
                    final_delete_button.click()
                    expect(page).to_have_url(f"{BASE_URL}/user/profile/")
                    error_field = page.locator("#error_delete_user").text_content()
                    assert error_field == "Invalid password"
                    break
                except Exception as e:
                    print(f"💀 2FA connexion failed {_ + 1} times , retrying💀", flush=True)
        else:
            password_field.fill("nope")
            final_delete_button.click()
            expect(page).to_have_url(f"{BASE_URL}/user/profile/")
            error_field = page.locator("#error_delete_user").text_content()
            assert error_field == "Invalid password"

        # ! CASE 2 INCORRECT OTP
        if user == "2fa":
            password_field = page.locator("#password")
            password_field.fill(PASSWORD)
            otp_field = page.locator("#otp-code")
            otp_field.fill("000000")

            final_delete_button.click()
            expect(page).to_have_url(f"{BASE_URL}/user/profile/")
            time.sleep(3)
            error_field = page.locator("#error_delete_user").text_content()
            
            assert error_field == "Invalid 2FA code"
        
        
        # ? HAPPY PATH : BOTH PASSWORD and OTP CORRECT
        if user == "2fa":
            for _ in range(3):
                current_code = totp.now()
                try:
                    password_field.fill(PASSWORD)
                    otp_field = page.locator("#otp-code")
                    otp_field.fill(current_code)
                    final_delete_button.click()
                    expect(page).to_have_url(f"{BASE_URL}/register/")
                    break
                except Exception as e:
                    print(f"💀 2FA connexion failed {_ + 1} times , retrying💀", flush=True)
        else:
            password_field.fill(PASSWORD)
            final_delete_button.click()
            expect(page).to_have_url(f"{BASE_URL}/register/")
        


    # ! =============== KICKSTART TESTER HERE ===============
    page.goto(f"{BASE_URL}/login/")
    delete_user("regular")
    page.goto(f"{BASE_URL}/login/")
    delete_user("2fa")

    # Those logins are supposed to fail
    page.goto(f"{BASE_URL}/login/")
    login("regular")
    error_message = page.locator("#login-form")
    expect(error_message).to_have_text("Invalid credentials")
    
    page.goto(f"{BASE_URL}/login/")
    login("2fa")
    error_message = page.locator("#login-form")
    expect(error_message).to_have_text("Invalid credentials")

    context.close()
    browser.close()

    print(f"✅ DELETE USER TEST ✅")


with sync_playwright() as playwright:
    run(playwright)
