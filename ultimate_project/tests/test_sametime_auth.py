from playwright.sync_api import Playwright, sync_playwright, expect
import time
import os
import pyotp


# USERS
LOGIN_REG = "same_auth"
LOGIN_2FA = "same_auth_2fa"
PASSWORD = "password"
SECRET_2FA = "AJUF2KESUQR45MRTL7MXDSJVI6JQDG42"

SIMULTANEOUS_USERS = 2

BASE_URL = "https://localhost:8443"




def run(playwright: Playwright) -> None:

    def get_ordinal_suffix(num):
        if num == 1:
            return "st"
        elif num == 2:
            return "nd"
        elif num == 3:
            return "rd"
        else:
            return "th"

    def get_screen_size():
        # This is a simple approach that works on many Linux systems
        # For more accurate results across all setups, consider a library like PyAutoGUI
        try:
            cmd = "xrandr | grep '*' | awk '{print $1}'"
            output = os.popen(cmd).read().strip().split("x")
            if len(output) == 2:
                return int(output[0]), int(output[1])
        except:
            pass
        # Fallback to common resolution
        return 1920, 1080

    def login(page, login, twofa = None):
        expect(page).to_have_url(f"{BASE_URL}/login/")

        # Fill in the username and password
        page.locator("#username").fill(login)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()

        time.sleep(2)

        if twofa:
            totp = pyotp.TOTP(SECRET_2FA)
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


        expect(page).to_have_url(f"{BASE_URL}/home/")

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
            browsers.append(
                playwright.chromium.launch(
                    headless=False,
                    args=[
                        f"--window-position={positions[_][0]},{positions[_][1]}",
                        f"--window-size={window_sizes[_][0]},{window_sizes[_][1]}",
                    ],
                )
            )

            # Create context with viewport size matching our target window size
            contexts.append(
                browsers[_].new_context(
                    ignore_https_errors=True,
                    viewport={
                        "width": window_sizes[_][0],
                        "height": window_sizes[_][1],
                    },
                )
            )

            pages.append(contexts[_].new_page())

            # Also set position via JavaScript to ensure it takes effect
            pages[_].evaluate(
                f"window.moveTo({positions[_][0]}, {positions[_][1]}); window.resizeTo({window_sizes[_][0]}, {window_sizes[_][1]});"
            )

    def destroy_obj(browsers, contexts):
        for context in contexts:
            context.close()
        for browser in browsers:
            browser.close()


    def test_reg_users(browsers, contexts, pages, positions, window_sizes):

        init_win(browsers, contexts, pages, positions, window_sizes)

        for _ in range(SIMULTANEOUS_USERS):
            pages[_].goto(f"{BASE_URL}/login/")
        
        page1 = pages[0]
        page2 = pages[1]

        # Page 1 login first
        login(page1, LOGIN_REG)

        # Page 1 Nagiguate the website
        page1.locator("#big-tournament").click()
        expect(page1).to_have_url(f"{BASE_URL}/tournament/tournament/")


        # Page 2 login after
        login(page2, LOGIN_REG)
        page2.locator("#big-tournament").click()
        expect(page2).to_have_url(f"{BASE_URL}/tournament/tournament/")

        
        # Page 1 tries to navigate afterwards, and is no longer auth
        page1.locator("#side-match").click()
        expect(page1).to_have_url(f"{BASE_URL}/register/")
        page1.goto(f"{BASE_URL}/home/")
        expect(page1).to_have_url(f"{BASE_URL}/register/")

        logout(page2)


        # time.sleep(10)

    def test_2fa_users(browsers, contexts, pages, positions, window_sizes):
        
        # init_win(browsers, contexts, pages, positions, window_sizes)
        
        for _ in range(SIMULTANEOUS_USERS):
            pages[_].goto(f"{BASE_URL}/login/")
        
        page1 = pages[0]
        page2 = pages[1]

        # Page 1 login first
        login(page1, LOGIN_2FA, "twofa")

        # Page 1 Nagiguate the website
        page1.locator("#big-tournament").click()
        expect(page1).to_have_url(f"{BASE_URL}/tournament/tournament/")

        # Page 2 login after
        login(page2, LOGIN_2FA, "twofa")
        page2.locator("#big-tournament").click()
        expect(page2).to_have_url(f"{BASE_URL}/tournament/tournament/")

        
        # Page 1 tries to navigate afterwards, and is no longer auth
        page1.locator("#side-match").click()
        expect(page1).to_have_url(f"{BASE_URL}/register/")
        page1.goto(f"{BASE_URL}/home/")
        expect(page1).to_have_url(f"{BASE_URL}/register/")
        
        # destroy_obj(browsers, contexts)
        

    # ! =============== INIT WINDOWS SIZES ===============
    browsers = []
    contexts = []
    pages = []
    

    screen_width, screen_height = get_screen_size()

    # Make windows narrow but tall (vertical shape)
    window_width = int(screen_width * 0.35)
    window_height = int(screen_height * 0.9)

    # Position one window at far left, one at far right
    left_position = 0
    right_position = screen_width - window_width

    # Position windows at left and right edges with different Y positions
    positions = [(left_position, 20), (right_position, 20)]

    # Set each window to be the same size
    window_sizes = [(window_width, window_height), (window_width, window_height)]

    # ! =============== KICKSTART TESTER HERE ===============
    test_reg_users(browsers, contexts, pages, positions, window_sizes)

    test_2fa_users(browsers, contexts, pages, positions, window_sizes)

    print(f"✅ SAMETIME AUTH PASSED ✅")

    destroy_obj(browsers, contexts)
    # context.close()
    # browser.close()


with sync_playwright() as playwright:
    run(playwright)
