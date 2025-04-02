from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter
import time

# USERS
USER_DE = "user2"
USER_EN = "user3"
USER_FR = "user4"
USER_ES = "user5"
USER_TL = "user6"

DE = "de"
EN = "en"
FR = "fr"
ES = "es"
TL = "tl"

STATS = [
    DE, "Statistiken",
    EN, "Statistics",
    FR, "Statistiques",
    ES, "Estadísticas",
    TL, "vItlhutlhmey",
]

PASSWORD = "password"

BASE_URL = "https://localhost:8443"


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True
    )
    page = context.new_page()

    def login(cur_login):
        expect(page).to_have_url(f"{BASE_URL}/login/")

        # Fill in the username and password
        page.locator("#username").fill(cur_login)
        page.locator("#password").fill(PASSWORD)
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

    def check_selector(lang):
        selector = page.locator("#language-selector").input_value()

        print(f"SELECTOR VALUE = {selector}")
        assert selector == lang, "WRONG SELECTOR VALUE"
        # assert selector == 'en', "WRONG SELECTOR VALUE"

    def change_selector(target):
        selector = page.locator("#language-selector")

        selector.select_option(target)

        page.wait_for_timeout(500)

        check_selector(target)

    def check_ids(lang):
        # Check ID navbar
        time.sleep(0.5)

        page_stats = page.locator("#stats-test").text_content().strip()
        dict_stats = STATS[STATS.index(lang) + 1].strip()
        
        assert page_stats == dict_stats, "WRONG ID STATS"



    def test_language(user, base_lang, target_lang):
        page.goto(f"{BASE_URL}/login/")

        login(user)

        check_selector(base_lang)

        check_ids(base_lang)

        change_selector(target_lang)

        check_ids(target_lang)

        logout()

    # ! =============== KICKSTART TESTER HERE ===============

    test_language(USER_DE, DE, ES)
    test_language(USER_DE, ES, DE)

    test_language(USER_EN, EN, FR)
    test_language(USER_EN, FR, EN)
    
    test_language(USER_FR, FR, TL)
    test_language(USER_FR, TL, FR)
    
    test_language(USER_ES, ES, DE)
    test_language(USER_ES, DE, ES)
    
    test_language(USER_TL, TL, EN)
    test_language(USER_TL, EN, TL)

    print(f"✅ LANGUAGE TESTS ✅")

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
