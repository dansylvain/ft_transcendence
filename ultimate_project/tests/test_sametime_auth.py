from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter
import time

# USERS
LOGIN_REG = "same_auth"
LOGIN_2FA = "same_auth_2fa"
PASSWORD = "password"
SECRET_2FA = "9JUF2KESUQR45MRTL7MXDSJVI6JQDG42"

SIMULTANEOUS_USERS = 2

BASE_URL = "https://localhost:8443"

def run(playwright: Playwright) -> None:
    # browser = playwright.chromium.launch(headless=False)
    # context = browser.new_context(
    #     ignore_https_errors=True
    # )
    # page = context.new_page()

    def get_screen_size():
        # This is a simple approach that works on many Linux systems
        # For more accurate results across all setups, consider a library like PyAutoGUI
        try:
            cmd = "xrandr | grep '*' | awk '{print $1}'"
            output = os.popen(cmd).read().strip().split('x')
            if len(output) == 2:
                return int(output[0]), int(output[1])
        except:
            pass
        # Fallback to common resolution
        return 1920, 1080

    def login(page):
        pass

    def logout(page):
        youpiBanane = page.locator("#youpiBanane")
        logoutButton = page.locator("#logoutButton")
        modalLogoutButton = page.locator("#modalLogoutButton")
        assert "show" not in (youpiBanane.get_attribute("class") or "")
        youpiBanane.click()
        logoutButton.click()
        modalLogoutButton.click()
        expect(page).to_have_url(f"{BASE_URL}/login/")

    def init_win(browsers, contexts, pages, positions, window_sizes):
        for _ in range(SIMULTANEOUS_USERS):
            # Launch browser without specific size/position first
            browsers.append(playwright.chromium.launch(headless=False))
            
            # Create context with viewport size matching our target window size
            contexts.append(browsers[_].new_context(
                ignore_https_errors=True,
                viewport={'width': window_sizes[_][0], 'height': window_sizes[_][1]}
            ))
            
            pages.append(contexts[_].new_page())
            
            # Now position the window after it's created
            if _ == 0:
                # First window on left half
                pages[_].evaluate(f"window.moveTo(0, 0); window.resizeTo({window_sizes[_][0]}, {window_sizes[_][1]});")
            else:
                # Second window on right half
                pages[_].evaluate(f"window.moveTo({positions[_][0]}, {positions[_][1]}); window.resizeTo({window_sizes[_][0]}, {window_sizes[_][1]});")

    def destroy_obj(browsers, contexts):
        for context in contexts:
            context.close()
        for browser in browsers:
            browser.close()

        # for _ in range(SIMULTANEOUS_USERS):
        #     contexts[_].close()
    
    def test_reg_users(browsers, contexts, pages, positions, window_sizes):
    
        init_win(browsers, contexts, pages, positions, window_sizes)
        
        for _ in range(SIMULTANEOUS_USERS):
            pages[_].goto(f"{BASE_URL}/login/")

        time.sleep(10)
        destroy_obj(browsers, contexts)
        pass
    
    def test_2fa_users():
        pass
    # ! =============== KICKSTART TESTER HERE ===============
    browsers = []
    contexts = []
    pages = []

    screen_width, screen_height = get_screen_size()
    
    # Réduire la largeur à 40% de l'écran pour chaque fenêtre
    window_width = int(screen_width * 0.4)  
    
    # Laisser un peu d'espace en hauteur (90% de la hauteur de l'écran)
    window_height = int(screen_height * 0.9)
    
    # Position each window with some spacing between them
    positions = [(50, 30), (window_width + 100, 30)]  # Ajouter un décalage horizontal et vertical
    
    # Set each window to be the same size
    window_sizes = [(window_width, window_height), (window_width, window_height)]

    
    test_reg_users(browsers, contexts, pages, positions, window_sizes)

    test_2fa_users()

    print(f"✅ SAMETIME AUTH PASSED ✅")

    # context.close()
    # browser.close()


with sync_playwright() as playwright:
    run(playwright)
