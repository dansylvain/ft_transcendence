from playwright.sync_api import Playwright, sync_playwright, expect
import time
import os
import pyotp
from playwright.async_api import async_playwright
import asyncio


# USERS
USER_2 = "user2"
USER_3 = "user3"
PASSWORD = "password"

SIMULTANEOUS_USERS = 2

BASE_URL = "https://localhost:8443"


def run(playwright: Playwright) -> None:

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

    def login(page, login, twofa=None):
        expect(page).to_have_url(f"{BASE_URL}/login/")

        # Fill in the username and password
        page.locator("#username").fill(login)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()

        time.sleep(2)

        # ! 2FA CONNEXION BLOCK
        # if twofa:
        #     totp = pyotp.TOTP(SECRET_2FA)
        #     expect(page).to_have_url(f"{BASE_URL}/two-factor-auth/")

        #     # Fill with a correct code
        #     for _ in range(3):
        #         current_code = totp.now()
        #         try:
        #             page.locator("#otp_input").fill(current_code)
        #             page.locator("#otp_verify").click()
        #             expect(page).to_have_url(f"{BASE_URL}/home/")
        #             print(
        #                 f"✅ 2FA connexion succed on {_ + 1}{get_ordinal_suffix(_ + 1)} try ✅",
        #                 flush=True,
        #             )
        #             break
        #         except Exception as e:
        #             print(f"💀 2FA connexion failed {_ + 1} times, retrying 💀", flush=True)

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
            if _ == 0:
                browsers.append(
                    playwright.chromium.launch(
                        headless=False,
                    )
                )
            else:
                browsers.append(
                    playwright.firefox.launch(
                        headless=False
                    )
                )

            # Create context with different settings for regular and incognito
            if _ == 0:
                # Regular browser context
                contexts.append(
                    browsers[_].new_context(
                        ignore_https_errors=True,
                    )
                )
            else:
                # Incognito-like browser context - explicitly don't persist cookies/storage
                contexts.append(
                    browsers[_].new_context(
                        ignore_https_errors=True,
                        storage_state=None,  # No stored cookies or localStorage
                    )
                )

            pages.append(contexts[_].new_page())

            # Added timeouts
            pages[_].set_default_timeout(20000) # 20 seconds timeout for Playright
            pages[_].set_default_navigation_timeout(20000) # # 20 seconds timeout for browser

    def destroy_obj(browsers, contexts):
        for context in contexts:
            context.close()
        for browser in browsers:
            browser.close()

    def routine_timer(page1, page2, which_winner = None, tournament_winner = None):

        # ! This routine check the timer appeance
        expect(page1.locator(".loader")).to_have_css("opacity", "1")
        expect(page2.locator(".loader")).to_have_css("opacity", "1")

        time.sleep(4.5)

        expect(page1.locator(".loader")).to_have_css("opacity", "0")
        expect(page2.locator(".loader")).to_have_css("opacity", "0")

        # Decide which player loose first
        # if not tournament_winner:
        if which_winner == "page1":
            # Page 1 click exit first, then he lose first
            page2.get_by_role("button", name="EXIT").click()
            time.sleep(1)
            if not tournament_winner:
                page1.get_by_role("button", name="EXIT").click()
        else:
            page1.get_by_role("button", name="EXIT").click()
            time.sleep(1)
            if not tournament_winner:
                page2.get_by_role("button", name="EXIT").click()
        
        if tournament_winner:
            time.sleep(1)
            message = page1.locator("#swal2-html-container").inner_text()
            # Expected text winner
            print(f" WON MESSAGE = {message}")

            expect(page1.locator("#swal2-html-container")).to_have_text(f"{tournament_winner} won the tournament!")
            expect(page2.locator("#swal2-html-container")).to_have_text(f"{tournament_winner} won the tournament!")

            # OK BUTTONS TO BE VISIBLE
            # class="swal2-confirm swal2-styled" => OK BUTTON

            page1.get_by_text("OK", exact=True).click()
            page2.get_by_text("OK", exact=True).click()
            # page1.locator(".swal2-confirm swal2-styled").click()
            # page2.locator(".swal2-confirm swal2-styled").click()

        # ID    swal2-html-container => user x won the tournament !
            # time.sleep(1000)
            # pass

    def test_remote_simple_match(pages):

        page1 = pages[0]
        page2 = pages[1]

        # Login both pages regular users

        # Page 1 Goes to match by clicking button... #! MAYBE NEED TO CHANGE THE LOCATOR
        page1.locator("#nav-match").click()
        # side-nav-tournament
        # page1.goto(f"{BASE_URL}/tournament/simple-match/")

        # Page 2 goes by straight link
        page2.goto(f"{BASE_URL}/tournament/simple-match/")

        # user2 send invite
        page1.get_by_text("user3").click()
        # user3 declines
        page2.get_by_role("button", name="Decline").click()
        # user2 accept user3 decline
        page1.get_by_role("button", name="OK").click()

        # user3 send invite
        page2.get_by_text("user2").click()
        # user2 Accept invite
        page1.get_by_role("button", name="Accept").click()

        # Both players enters match
        page1.get_by_text("match:").click()
        page2.get_by_text("match:").click()

        # Timer routine checking
        routine_timer(page1, page2)


    def launch_tournament(page1, page2, match2_player2, match3_player1, match3_player2):
        
        # user2 tries to move a non player of him
        source1 = page1.get_by_text(match3_player1, exact=True)
        target1 = page1.locator(".tournament-cont")
        source1.drag_to(target1)
        time.sleep(0.5)
        expect(page1.locator("#swal2-html-container")).to_have_text("Not your player!")
        page1.get_by_text("OK", exact=True).click()

        # user3 tries to move a non player of him
        source2 = page2.get_by_text(match3_player2, exact=True)
        target2 = page2.locator(".tournament-cont")
        source2.drag_to(target2)
        time.sleep(0.5)
        expect(page2.locator("#swal2-html-container")).to_have_text("Not your player!")
        page2.get_by_text("OK", exact=True).click()

        print(f"TRY 1")

        # User3 move his ghost...
        source2 = page2.get_by_text(match2_player2, exact=True)
        target2 = page2.locator(".tournament-cont")
        source2.drag_to(target2)
        print(f"TRY 2")

        # time.sleep(10)

        # ... and himself
        # source2 = page2.locator(".user self-player")

        # source3 = page2.get_by_text(match3_player1, exact=True)

        source3 = page2.locator(f"div[draggable='true'].user.self-player:has-text('{match3_player1}')")

        # source3 = page2.locator(".user self-player")
        # page.locator("[id=\"\\33 \"]").click()
        target3 = page2.locator(".tournament-cont")
        source3.drag_to(target3)
        print(f"TRY 3")

        # User 2 moves his ghost
        source1 = page1.get_by_text(match3_player2, exact=True)
        target1 = page1.locator(".tournament-cont")
        source1.drag_to(target1)
        print(f"TRY 4")

    def test_remote_tournament(pages):

        page1 = pages[0]
        page2 = pages[1]

        # Page 1 Goes to match by clicking button... #! NEED TO SWITCH SELECTORS ONCE FINISHED
        page1.goto(f"{BASE_URL}/tournament/tournament/")
        # page1.locator("#side-nav-tournament").click()

        # Page 2 goes by straight link
        page2.goto(f"{BASE_URL}/tournament/tournament/")

        match2_player2 = "ghost_user3"
        match3_player1 = USER_3
        match3_player2 = "ghost_user2"

        page1.locator("#player-name").fill(match3_player2)
        page2.locator("#player-name").fill(match2_player2)

        page1.get_by_text("Add Player", exact=True).click()
        page2.get_by_text("Add Player", exact=True).click()

        page1.get_by_role("button", name="Create Tournament").click()

        launch_tournament(page1, page2, match2_player2, match3_player1, match3_player2)

        # ! ================== WORK NEEEEEEEDLE ===================

        # Launch Match 1 user2 vs ghost_user3
        page1.locator("#m2").click()
        page2.locator("#m2").click()
        routine_timer(page1, page2, "page1")

        print("MATCH 1 DONE")
        time.sleep(2)

        # Launch Match 2 user3 vs ghost_user2
        page1.locator("#m3").click()
        page2.locator("#m3").click()
        routine_timer(page1, page2, "page2")
        print("MATCH 2 DONE")

        time.sleep(2)
        # Launch Final Match user2
        page1.locator("#m1").click()
        page2.locator("#m1").click()
        routine_timer(page1, page2, "page2", "user3")
        print("FINALE DONE")

        # time.sleep(1000)


    # ! =============== INIT WINDOWS SIZES ===============
    browsers = []
    contexts = []
    pages = []

    screen_width, screen_height = get_screen_size()

    # Make windows narrow but tall (vertical shape)
    window_width = int(screen_width)
    window_height = int(screen_height)

    # Position one window at far left, one at far right
    left_position = 0
    right_position = screen_width - window_width

    # Position windows at left and right edges with different Y positions
    positions = [(left_position, 20), (right_position, 20)]

    # Set each window to be the same size
    window_sizes = [(window_width, window_height), (window_width, window_height)]

    # Initialize windows before running tests
    init_win(browsers, contexts, pages, positions, window_sizes)

    # ! =============== KICKSTART TESTER HERE ===============
    for _ in range(SIMULTANEOUS_USERS):
        pages[_].goto(f"{BASE_URL}/login/")

    login(pages[0], USER_2)
    login(pages[1], USER_3)

    test_remote_simple_match(pages)

    test_remote_tournament(pages)

    print(f"✅ GAME TESTS ✅")

    destroy_obj(browsers, contexts)

    # context.close()
    # browser.close()


with sync_playwright() as playwright:
    run(playwright)
