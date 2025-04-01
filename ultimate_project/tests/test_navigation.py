from playwright.sync_api import Playwright, sync_playwright, expect
import time

def run(playwright: Playwright) -> None:
    base_url = "https://localhost:8443"
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True
    )
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
        navigate(f"{base_url}/user/account/profile/")
        navigate(f"{base_url}{url}")
        page.evaluate("window.history.back()")
        page.wait_for_timeout(500)  # Laisse un peu de temps pour le back
        test_page(page.url)

    urls = [ 
            f"{base_url}/home/", 
            f"{base_url}/account/profile/", 
            f"{base_url}/account/game-stats/",
            f"{base_url}/tournament/simple-match/",
            f"{base_url}/tournament/tournament/"
            ]     
    
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
        ("#nav-profile", f"{base_url}/account/profile/"),
        ("#nav-stats", f"{base_url}/account/game-stats/"),
        ("#nav-match", f"{base_url}/tournament/simple-match/"),
        ("#side-tournoi", f"{base_url}/tournament/tournament/"),
        ("#side-profile", f"{base_url}/account/profile/"),
        ("#side-stats", f"{base_url}/account/game-stats/"),
        ("#side-match", f"{base_url}/tournament/simple-match/"),
        ("#field-tournoi", f"{base_url}/tournament/tournament/"),
        ("#field-match", f"{base_url}/tournament/simple-match/"),
        ("#field-profile", f"{base_url}/account/profile/"),
        ("#field-stats", f"{base_url}/account/game-stats/"),
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

    print(f"✅ NAVIGATION TEST ✅")



with sync_playwright() as playwright:
    run(playwright)
