# ! IMPORTANT : For register AND login testing purposes, you need to create a user with the following credentials :
# !  USERNAME : test
# !  EMAIL : test@test.com
# !  PASSWORD : password

from playwright.sync_api import Playwright, sync_playwright, expect
import time


def run(playwright: Playwright) -> None:
    base_url = "http://localhost:8000"
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    visited_urls = []
    page.set_default_timeout(6000) # Timeout of 6 seconds for each click

    # Fonction de navigation avec attente
    def navigate(url: str):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        visited_urls.append(url)

    # test du toggle de la sidebar
    def check_sidebar_Toggle():
        sidebar = page.locator("#accordionSidebar")
        toggle_button = page.locator("#sidebarToggle")
        if not toggle_button.is_visible():
            return
        assert "toggled" not in (sidebar.get_attribute("class") or "")
        toggle_button.click()
        assert "toggled" in (sidebar.get_attribute("class") or "")
        toggle_button.click()
        assert "toggled" not in (sidebar.get_attribute("class") or "")

    #test du toggle du dheckout_modal
    def check_checkout_modal_Toggle():
        logoutModal = page.locator("#youpiBanane")
        assert "show" not in (logoutModal.get_attribute("class") or "")
        logoutModal.click()
        assert "show" in (logoutModal.get_attribute("class") or "")
        logoutModal.click()
        assert "show" not in (logoutModal.get_attribute("class") or "")

    #test du bouton logout
    def check_checkout_button():
        youpiBanane = page.locator("#youpiBanane")
        logoutButton = page.locator("#logoutButton")
        modalLogoutButton = page.locator("#modalLogoutButton")
        assert "show" not in (youpiBanane.get_attribute("class") or "")
        youpiBanane.click()
        logoutButton.click()
        modalLogoutButton.click()
        expect(page).to_have_url(f"{base_url}/login/")

        # expect(page).to_have_url(f"{base_url}/login/")
    def test_js():
        check_sidebar_Toggle()
        check_checkout_modal_Toggle()
        check_checkout_button()

    def test_page(url: str):
        if url:
            navigate(url)
            visited_urls.append(url)  # Enregistre l'URL après chaque navigation
        test_js()

    def test_single_page(url: str):
        navigate(f"{base_url}/user/profile/")
        navigate(f"{base_url}{url}")
        page.evaluate("window.history.back()")
        page.wait_for_timeout(500)  # Laisse un peu de temps pour le back
        test_page(page.url)
    

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
        context = browser.new_context()
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


    urls = [ 
            f"{base_url}/home/", 
            f"{base_url}/user/profile/", 
            f"{base_url}/user/stats/",
            f"{base_url}/tournament/simple-match/",
            f"{base_url}/tournament/tournament/"
            ]     
    
    # ! =============== KICKSTART TESTER HERE ===============
    
    # Those tests create, test and close their own browsers
    # register_from_login()
    # register_after_login()


    # ? =============== START REGULAR TESTS ===============
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(f"{base_url}/register/")
    
    # Regular register + login tests which links to Dan tests after getting proprely logged-in
    # test_register(base_url, page)
    # test_login(base_url, page)

    # DAN TEST FROM HERE
    for url in urls:
        test_page(url)
    
    for url in urls:
        navigate(url)

    for url in reversed(urls):
        while True:
            if page.url == url:
                test_js()
                page.wait_for_timeout(500)
                break
            else:
                page.evaluate("window.history.back()")
                page.wait_for_timeout(500)  # Laisse un peu de temps pour le back
                visited_urls.remove(url)
                

    # Vérification de la navigation via le sidebar menu
    def test_navigation(locator, expected_url):
        locator.click()
        expect(page).to_have_url(expected_url)

    # Liste des tests à effectuer
    navigation_tests = [
        ("#nav-tournoi", f"{base_url}/tournament/tournament/"),
        ("#nav-profile", f"{base_url}/user/profile/"),
        ("#nav-stats", f"{base_url}/user/stats/"),
        ("#nav-match", f"{base_url}/tournament/simple-match/"),
        ("#side-tournoi", f"{base_url}/tournament/tournament/"),
        ("#side-profile", f"{base_url}/user/profile/"),
        ("#side-stats", f"{base_url}/user/stats/"),
        ("#side-match", f"{base_url}/tournament/simple-match/"),
        ("#field-tournoi", f"{base_url}/tournament/tournament/"),
        ("#field-match", f"{base_url}/tournament/simple-match/"),
        ("#field-profile", f"{base_url}/user/profile/"),
        ("#field-stats", f"{base_url}/user/stats/"),
    ]

    # Vérification de la navigation via le menu topbar
    navigate(f"{base_url}/home/")
    for locator, expected_url in navigation_tests[:4]:  # Pour les éléments du menu topbar
        test_navigation(page.locator(locator), expected_url)

    # Vérification de la navigation via le menu latéral
    for locator, expected_url in navigation_tests[4:8]:  # Pour les éléments du menu latéral
        test_navigation(page.locator(locator), expected_url)

    # Vérification de la navigation via les boutons sur la page home
    for locator, expected_url in navigation_tests[8:]:  # Pour les éléments de la page home
        navigate(f"{base_url}/home/")
        test_navigation(page.locator(locator), expected_url)
    # test 404

    test_single_page("/home/sylvain_duriff/");
    test_single_page("/register/")



    # Fermeture
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)

# def run(playwright: Playwright) -> None:
#     browser = playwright.chromium.launch(headless=False)
#     context = browser.new_context()
#     page = context.new_page()
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/")
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/home/")
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/user/profile/")
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/user/stats/")
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/tournament/simple-match/")
#     time.sleep(0.4)
#     page.locator("#nav-home").click()
#     time.sleep(0.4)
#     page.locator("#nav-tournament").click()
#     time.sleep(0.4)
#     page.locator("#nav-profile").click()
#     time.sleep(0.4)
#     page.locator("#nav-stats").click()
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/home/")
#     page.locator("#field-tournament").click()
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/home/")
#     page.locator("#field-profile").click()
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/home/")
#     page.locator("#field-stats").click()
#     time.sleep(0.4)

#     # ---------------------
#     context.close()
#     browser.close()


# with sync_playwright() as playwright:
#     run(playwright)


# # import re
# from playwright.sync_api import Playwright, sync_playwright  # , expect

# import time


# def run(playwright: Playwright) -> None:
#     browser = playwright.chromium.launch(headless=False)
#     context = browser.new_context()
#     page = context.new_page()

#     # Loguer toutes les requêtes effectuées
#     def handle_request(request):
#         print(f"➡️ Requête envoyée : {request.url}")

#     # Loguer toutes les réponses reçues
#     def handle_response(response):
#         print(f"⬅️ Réponse reçue : {response.url} - Statut: {response.status}")
#         if response.status == 404:
#             print(f"❌ Erreur 404 détectée pour : {response.url}")

#     page.on("request", handle_request)
#     page.on("response", handle_response)

#     page.on("response", handle_response)

#     page.goto("http://localhost:8000/")
#     time.sleep(0.4)
#     page.get_by_role("textbox", name="Entrez votre nom").click()
#     time.sleep(0.4)
#     page.get_by_role("textbox", name="Entrez votre nom").fill("kapouet")
#     time.sleep(0.4)
#     page.get_by_role("button", name="Connexion").click()
#     time.sleep(0.4)
#     page.get_by_role("button", name="Tournament").click()
#     time.sleep(0.4)
#     page.get_by_role("button", name="Close").click()
#     time.sleep(0.4)
#     page.get_by_role("button", name="Simple Match").click()
#     time.sleep(0.4)
#     page.get_by_role("button", name="Close").click()
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/test/")
#     time.sleep(0.4)
#     page.goto("http://localhost:8000/match/")

#     # TEST FLO
#     time.sleep(1)
#     page.goto("http://localhost:8000/user/")
#     time.sleep(1)
#     # TEST FLO
#     websocket_connected = False
#     time.sleep(0.4)

#     def handle_websocket(ws):
#         nonlocal websocket_connected
#         websocket_connected = True
#         print(f"🔌 WebSocket connectée à : {ws.url}")

#     page.on("websocket", handle_websocket)
#     page.goto("http://localhost:8000/match/")
#     try:
#         if websocket_connected:
#             print("✅ La connexion WebSocket est réussie.")
#         else:
#             raise ValueError("❌ La connexion WebSocket a échoué.")
#     except ValueError as e:
#         print(e)

#     # ---------------------
#     context.close()
#     browser.close()


# with sync_playwright() as playwright:
#     run(playwright)
