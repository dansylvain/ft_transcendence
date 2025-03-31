from playwright.sync_api import Playwright, sync_playwright, expect
import time

def run(playwright: Playwright) -> None:
    base_url = "https://localhost:8443"
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True
    )
    page = context.new_page()

    def test_login(base_url: str, page):

        # Test de la page d'accueil avec une fausse connexion
        # page.goto(f"{base_url}/login/")
        expect(page).to_have_url(f"{base_url}/login/")
        page.locator("#username").fill("sylvain_duriff")
        page.locator("#password").fill("wrong_password")
        page.locator("#loginButton").click()
        error_message = page.locator("#login-form")
        expect(error_message).to_have_text("Invalid credentials")

        # Test de la page d'accueil avec une vraie connexion
        page.locator("#username").fill("test")
        page.locator("#password").fill("password")
        page.locator("#loginButton").click()
        expect(page).to_have_url(f"{base_url}/home/")
    

    def current_register_test(page, target_field: str, incorrect_data: str, expected_error: str):
        # Correct register credentials
        correct_first_name = "Sylvain"
        correct_last_name = "Duriff"
        correct_email = "example@hehe.com"
        correct_username = "sylvain_duriff"
        correct_password = "password"

        # Fill with valid data
        page.locator("#first_name").fill(correct_first_name)
        page.locator("#last_name").fill(correct_last_name)
        page.locator("#username").fill(correct_username)
        page.locator("#email").fill(correct_email)
        page.locator("#password").fill(correct_password)
        page.locator("#repeat_password").fill(correct_password)
        
        # Fill with the incorrect data at the targeted field
        page.locator(f"#{target_field}").fill(incorrect_data)
        
        # If testing for password regex, fill the `repeat_password` as well
        if target_field == "password":
            page.locator(f"#repeat_password").fill(incorrect_data)
        
        # Click the register button
        page.locator("#register-button").click()
        error_message = page.locator("#register-form")
        
        # Check if the targeted error is the one we expect
        expect(error_message).to_have_text(expected_error)
        time.sleep(0.2)

    def test_register(base_url: str, page):

        correct_email = "example@hehe.com"
        incorrect_email = "example@hehe"
        taken_email = "test@test.com"
        
        # Shitty register credentials
        incorrect_first_name = "??|"
        incorrect_last_name = "??|"
        incorrect_username = "%&?аAAAaaaа" # * this `а` is a cyrilic alphabet character 
        incorrect_password = "///"

        taken_username = "test"

        # Expected error messages from the backend
        expected_error_firstname = "Forbidden characters in first name. Allowed characters: a-z, A-Z, 0-9, -, _"
        expected_error_lastname = "Forbidden characters in last name. Allowed characters: a-z, A-Z, 0-9, -, _"
        expected_error_username = "Forbidden characters in username. Allowed characters: a-z, A-Z, 0-9, -, _"
        expected_error_password = "Forbidden characters in password. Allowed characters: a-z, A-Z, 0-9, -, _, !, ?, $, €, %, &, *, (, )"
        expected_error_taken_username = "Username already taken."
        expected_error_taken_email = "Email adress already taken."
        
        # ! TESTING BACKEND REGEX FOR REJECTING FIELDS WITH NON ACCEPTED CHARACTERS
        # Test first name
        current_register_test(page, "first_name", incorrect_first_name, expected_error_firstname)
        # Test last name
        current_register_test(page, "last_name", incorrect_last_name, expected_error_lastname)
        # Test wrong username name
        current_register_test(page, "username", incorrect_username, expected_error_username)
        # Test wrong password
        current_register_test(page, "password", incorrect_password, expected_error_password)

        # ! TESTING ALREADY EXISTING USERS / EMAIL
        # Test already taken username
        current_register_test(page, "username", taken_username, expected_error_taken_username)
        # Test already taken email
        current_register_test(page, "email", taken_email, expected_error_taken_email)

        # ! TESTING CSS FOR EMAIL
        page.locator("#email").fill(incorrect_email)
        assert page.is_visible("#email-error")
        email_classes = page.get_attribute("#email", "class") or ""
        assert "is-invalid" in email_classes.split(), "Expected 'is-invalid' class to be applied"

        page.locator("#email").fill(correct_email)
        assert not page.is_visible("#email-error")
        email_classes = page.get_attribute("#email", "class") or ""
        assert "is-invalid" not in email_classes.split(), "Did not expect 'is-invalid' class to be applied"

        # ! TESTING CSS PASSWORD DO NOT MATCH APPEARS
        page.locator("#repeat_password").fill("nope")
        assert page.is_visible("#password-error")
        page.locator("#repeat_password").fill("password")
        assert not page.is_visible("#password-error")

        # ! TESTING PASSWORD STRENGHT BAR
        test_cases = [
            ("", "progress-bar", "Password strength: Not entered"),
            ("a", "bg-danger", "Password strength: Weak"),
            ("password", "bg-warning", "Password strength: Medium"),
            ("password1", "bg-info", "Password strength: Strong"),
            ("password1A!", "bg-success", "Password strength: Very strong"),
        ]

        for password, expected_class, expected_text in test_cases:
            page.locator("#password").fill("")
            page.locator("#password").fill(password)
            page.dispatch_event("#password", "input")
            page.wait_for_timeout(200)

            # Assert correct class
            classes = page.locator("#password-strength-bar").get_attribute("class") or ""
            assert expected_class in classes.split(), f"Expected class '{expected_class}' for password '{password}', got: {classes}"

            # Assert correct message
            text = page.locator("#password-strength-text").text_content().strip()
            assert text == expected_text, f"Expected text '{expected_text}' for password '{password}', got: '{text}'"
        
        page.locator("#login-link").click()
    
    def register_from_login():
        page.goto(f"{base_url}/login/")
        register_button = page.locator("#register-link")
        register_button.click()
        expect(page).to_have_url(f"{base_url}/register/")
        
        test_register(base_url, page)
        
        context.close()
        browser.close()
    
    def register_after_login():
        # Starting a new window
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(
        ignore_https_errors=True
    )
        page = context.new_page()
        
        # Register testing comming from within the website
        page.goto(f"{base_url}/login/")
        page.locator("#username").fill("test")
        page.locator("#password").fill("password")
        page.locator("#loginButton").click()
        expect(page).to_have_url(f"{base_url}/home/")
        
        # Loggin out
        youpiBanane = page.locator("#youpiBanane")
        logoutButton = page.locator("#logoutButton")
        modalLogoutButton = page.locator("#modalLogoutButton")
        assert "show" not in (youpiBanane.get_attribute("class") or "")
        youpiBanane.click()
        logoutButton.click()
        modalLogoutButton.click()
        expect(page).to_have_url(f"{base_url}/login/")

        register_button = page.locator("#register-link")
        register_button.click()
        expect(page).to_have_url(f"{base_url}/register/")
        
        test_register(base_url, page)
        
        context.close()
        browser.close()

    # ! =============== KICKSTART TESTER HERE ===============
    
    # Those tests create, test and close their own browsers
    register_from_login()
    register_after_login()
    # test_login_2fa(playwright) # ! NOT YET READY
    # test_register_2fa(playwright) # ! NOT YET READY

    # ? =============== START REGULAR TESTS ===============
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True
    )
    page = context.new_page()
    page.goto(f"{base_url}/register/")
    
    # Regular register + login tests which links to Dan tests after getting proprely logged-in
    test_register(base_url, page)
    test_login(base_url, page)

    print(f"✅ AUTHENTICATION TESTS PASSED ✅")


with sync_playwright() as playwright:
    run(playwright)
