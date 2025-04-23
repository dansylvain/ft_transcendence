from playwright.sync_api import Playwright, sync_playwright, expect
from collections import Counter
import time

# USERS
LOGIN = "user2"
PASSWORD = "password"

BASE_URL = "https://localhost:8443"


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        ignore_https_errors=True,
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()

    # Added timeouts
    page.set_default_timeout(20000) # 20 seconds timeout for Playright
    page.set_default_navigation_timeout(20000) # # 20 seconds timeout for browser

    def login():
        expect(page).to_have_url(f"{BASE_URL}/login/")

        # Fill in the username and password
        page.locator("#username").fill(LOGIN)
        page.locator("#password").fill(PASSWORD)
        page.locator("#loginButton").click()


    def logout():
        youpiBanane = page.locator("#youpiBanane")
        logoutButton = page.locator("#logoutButton")
        modalLogoutButton = page.locator("#modalLogoutButton")
        assert "show" not in (youpiBanane.get_attribute("class") or "")
        youpiBanane.click()
        logoutButton.click()
        modalLogoutButton.click()
        expect(page).to_have_url(f"{BASE_URL}/login/")

    def test_local_match():

        page.goto(f"{BASE_URL}/login/")

        login()

        expect(page).to_have_url(f"{BASE_URL}/home/")
        
        page.goto(f"{BASE_URL}/tournament/simple-match/")
        
        # This block is registered by auto-playright
        page.get_by_text("user2", exact=True).click()
        page.get_by_role("textbox", name="enter a name").click()
        page.get_by_role("textbox", name="enter a name").fill("bobby")
        page.get_by_text("user2", exact=True).click()
        page.get_by_text("match:").click()
        expect(page.locator('.loader')).to_have_css('opacity', '1')
        time.sleep(5)
        expect(page.locator('.loader')).to_have_css('opacity', '0')
        page.get_by_role("button", name="EXIT").click()

        page.locator("#side-nav-tournament").click()
        time.sleep(0.1)

        page.locator("#side-nav-simple-match").click()
        time.sleep(1)

        page.get_by_text("user2", exact=True).click()
        page.get_by_role("textbox", name="enter a name").click()
        page.get_by_role("textbox", name="enter a name").fill("bobby")
        page.get_by_text("user2", exact=True).click()
        page.get_by_text("match:").click()
        expect(page.locator('.loader')).to_have_css('opacity', '1')
        time.sleep(5)
        expect(page.locator('.loader')).to_have_css('opacity', '0')
        page.get_by_role("button", name="EXIT").click()


        page.goto(f"{BASE_URL}/tournament/tournament/")
        time.sleep(3)
        page.locator("#player-name").click()
        time.sleep(0.1)
        page.get_by_role("textbox", name="enter a name").fill("hehe")
        time.sleep(0.1)
        page.get_by_text("Add Player", exact=True).click()
        time.sleep(0.1)
        page.locator("#player-name").click()
        time.sleep(0.1)
        page.get_by_role("textbox", name="enter a name").fill("haha")
        time.sleep(0.1)
        page.get_by_text("Add Player", exact=True).click()
        time.sleep(0.1)
        page.locator("#player-name").click()
        time.sleep(0.1)
        page.get_by_role("textbox", name="enter a name").fill("hoho")
        time.sleep(0.1)
        page.get_by_text("Add Player", exact=True).click()
        time.sleep(0.1)
        
        page.get_by_text("Create Tournament").click()
        
        source = page.get_by_text("hehe")
        target = page.locator(".tournament-cont")
        source.drag_to(target)
        source = page.get_by_text("haha")
        target = page.locator(".tournament-cont")
        source.drag_to(target)
        source = page.get_by_text("hoho")
        target = page.locator(".tournament-cont")
        source.drag_to(target)

        page.locator("#m2").click()
        time.sleep(0.1)
        expect(page.locator('.loader')).to_have_css('opacity', '1')
        time.sleep(5)
        expect(page.locator('.loader')).to_have_css('opacity', '0')
        time.sleep(0.1)
        page.get_by_role("button", name="EXIT").click()
        time.sleep(0.1)
        
        page.locator("#m3").click()
        time.sleep(0.1)
        expect(page.locator('.loader')).to_have_css('opacity', '1')
        time.sleep(5)
        expect(page.locator('.loader')).to_have_css('opacity', '0')
        time.sleep(0.1)
        page.get_by_role("button", name="EXIT").click()
        time.sleep(0.1)

        page.locator("#m1").click()
        time.sleep(0.1)
        expect(page.locator('.loader')).to_have_css('opacity', '1')
        time.sleep(5)
        expect(page.locator('.loader')).to_have_css('opacity', '0')
        time.sleep(0.1)
        page.get_by_role("button", name="EXIT").click()
        time.sleep(0.1)
        page.get_by_text("OK", exact=True).click()
        time.sleep(0.1)

        page.locator("#side-nav-simple-match").click()
        time.sleep(1)

        page.locator("#side-nav-tournament").click()
        time.sleep(0.1)

        time.sleep(3)
        page.locator("#player-name").click()
        time.sleep(0.1)
        page.get_by_role("textbox", name="enter a name").fill("hehe")
        time.sleep(0.1)
        page.get_by_text("Add Player", exact=True).click()
        time.sleep(0.1)
        page.locator("#player-name").click()
        time.sleep(0.1)
        page.get_by_role("textbox", name="enter a name").fill("haha")
        time.sleep(0.1)
        page.get_by_text("Add Player", exact=True).click()
        time.sleep(0.1)
        page.locator("#player-name").click()
        time.sleep(0.1)
        page.get_by_role("textbox", name="enter a name").fill("hoho")
        time.sleep(0.1)
        page.get_by_text("Add Player", exact=True).click()
        time.sleep(0.1)
        
        page.get_by_text("Create Tournament").click()
        
        source = page.get_by_text("hehe")
        target = page.locator(".tournament-cont")
        source.drag_to(target)
        source = page.get_by_text("haha")
        target = page.locator(".tournament-cont")
        source.drag_to(target)
        source = page.get_by_text("hoho")
        target = page.locator(".tournament-cont")
        source.drag_to(target)

        page.locator("#m2").click()
        time.sleep(0.1)
        expect(page.locator('.loader')).to_have_css('opacity', '1')
        time.sleep(5)
        expect(page.locator('.loader')).to_have_css('opacity', '0')
        time.sleep(0.1)
        page.get_by_role("button", name="EXIT").click()
        time.sleep(0.1)
        
        page.locator("#m3").click()
        time.sleep(0.1)
        expect(page.locator('.loader')).to_have_css('opacity', '1')
        time.sleep(5)
        expect(page.locator('.loader')).to_have_css('opacity', '0')
        time.sleep(0.1)
        page.get_by_role("button", name="EXIT").click()
        time.sleep(0.1)

        page.locator("#m1").click()
        time.sleep(0.1)
        expect(page.locator('.loader')).to_have_css('opacity', '1')
        time.sleep(5)
        expect(page.locator('.loader')).to_have_css('opacity', '0')
        time.sleep(0.1)
        page.get_by_role("button", name="EXIT").click()
        time.sleep(0.1)
        page.get_by_text("OK", exact=True).click()
        time.sleep(0.1)

        """
        - TEST QUATRE: test tournament one machine
        - l'user navigue vers la page tournament✅
        - ROUTINE (x3): Dans le champ avec l'id="player-name", il entre les noms "hehe", "hoho", "haha"✅
        - il clique sur l'élément dont le contenu est "Add Player"✅
        - il clique sur l'élément dont le contenu est "Create Tournament"✅
        - il drag and drop les trois divs avec les classes "user phantom" et enfants du div id="players"
            vers le div avec la class="tournament-cont"✅
        - il clique sur le div avec l'id="m2"✅
        - => SUBROUTINE 1✅
        - il clique sur le div avec l'id="m3"✅
        - => SUBROUTINE 1✅
        - il clique sur le div avec l'id="m1"✅
        - => SUBROUTINE 1✅
        - ✅
        """








        logout()

    # ! =============== KICKSTART TESTER HERE ===============

    test_local_match()

    print(f"✅ LOCAL GAMES TEST OKAY ✅")

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)


    """
    DAN, PUT WHAT TO TEST HERE

    - TEST MATCH SIMPLE ✅
    - PREMIER TEST: test 1v1 solo✅
    - Navigate to page Match simple✅

    - START ROUTINE1 click sur l'element ayant les classes "user self-player" ✅
    - dans l'input avec l'id="match-player-name", entre le nom "bobby"✅
    - click ENCORE sur le meme elment qu'avant ✅
    
    
    - START ROUTINE 2 click sur l'element avec les classes "match self-match"   ✅ - 
    - l'élément avec la class "loader" doit avoir style="opacity: 1;"✅
    - attendre 4 secondes✅
    - l'élément avec la class "loader" doit avoir style="opacity: 0;"✅
    - 
    - DEUXIEME TEST:  test 1v1 solo part 2✅
    - cliquer sur l'élément avec id="acc-profile" (on va devoir changer cet id, c'ets le template de thomas :)✅
    - cliquer sur l'élément avec id="acc-profile" (on revient sur la page via une htmx)✅
    - On rebalance le test a partir de START ROUTINE1✅

    ✅
    - TEST TROIS: test 1v1 remote
    - on ouvre deux sessions avec deux user differents ✅
    - un des deux users acced a la page match simple par un click sur l'élément avec id="acc-profile" ✅ 
    - l'autre navigue directement à la page ✅
    - joueur A clique sur l'élément avec la classe "user" (et UNIQUEMENT la classe user)
    - joueur B clique sur l'élément avec les classe "swal2-cancel swal2-styled"
    - l'autre A clique sur l'élément avec les classes "swal2-confirm swal2-styled"
    - joueur B clique sur l'élément avec la classe "user" (et UNIQUEMENT la classe user)
    - joueur A clique sur l'élément avec les classes "swal2-confirm swal2-styled"
    - joueur A et joueur B excuent la routine 2
 
    - TEST QUATRE: test tournament one machine
    - l'user navigue vers la page tournament
    - ROUTINE (x3): Dans le champ avec l'id="player-name", il entre les noms "hehe", "hoho", "haha"
    - il clique sur l'élément dont le contenu est "Add Player"
    - il clique sur l'élément dont le contenu est "Create Tournament"
    - il drag and drop les trois divs avec les classes "user phantom" et enfants du div id="players"
        vers le div avec la class="tournament-cont"
    - il clique sur le div avec l'id="m2"
    - => SUBROUTINE 1
    - il clique sur le div avec l'id="m3"
    - => SUBROUTINE 1
    - il clique sur le div avec l'id="m1"
    - => SUBROUTINE 1
    - 
    -

    - TEST CINQ: test tournament remote
    - on lance deux navigateurs
    - l'user A navigue vers la page tournament
    - l'user A clique sur le lien vers la page tournament
    - Dans le champ avec l'id="player-name", chacun d'entre eux entre les noms "hehe" OU "hoho"
    - chacun d'entre eux clique sur l'élément dont le contenu est "Add Player"
    - chacun d'entre eux clique sur l'élément dont le contenu est "Create Tournament"
    - chacun d'entre eux drag and drop le div avec les classes "user phantom" et enfant du div id="players"
        vers le div avec la class="tournament-cont"
    
    - apres, c'est la merde...

    
    """