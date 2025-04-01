from playwright.sync_api import Playwright, sync_playwright
import time



def navigate(page, url: str):
    page.goto(url)
    page.wait_for_load_state("networkidle")


def run(playwright: Playwright) -> None:
    base_url = "https://localhost:8443"
    browsers = []
    contexts = []
    pages = []

    # Positions des fenêtres (2 par ligne)
    positions = [(0, 0), (800, 0), (0, 600), (800, 600)]

    # URLs
    urls = [ 
        f"{base_url}/login/", 
        f"{base_url}/tournament/simple-match/",
        f"{base_url}/tournament/tournament/"
    ]    

    utilisateurs = {
        "user2": "password",
        "user3": "password",
        "user4": "password",
        "user5": "password"
    }

    for i, (x, y) in enumerate(positions):
        browser = playwright.chromium.launch(
            headless=False,
            args=[f"--window-position={x},{y}", "--window-size=800,600"]
        )
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.set_default_timeout(6000)
        page.goto(urls[0])
        page.wait_for_load_state("networkidle")

        # Remplir les champs de connexion
        username_input = page.locator("input[name='username']")
        password_input = page.locator("input[name='password']")
        login_button = page.locator("input[type='submit'][id='loginButton']")

        user_key = list(utilisateurs.keys())[i % len(utilisateurs)]
        username_input.fill(user_key)
        password_input.fill(utilisateurs[user_key])

        # Cliquer sur le bouton de connexion
        login_button.click()
        page.wait_for_load_state("networkidle")

        # Cliquer sur le lien tournoi
        tournament_page_link = page.locator("#nav-tournoi")
        tournament_page_link.click()

        # Clique sur "Create" pour la première fenêtre seulement
        if i == 0:
            try:
                page.click('button[onclick="newTournament(window.tournamentSocket)"]')
                print("✔️ Fenêtre 1 : Bouton 'Create' cliqué")
            except:
                print("❌ Fenêtre 1 : Bouton 'Create' non trouvé")

        # Clique sur un élément utilisateur pour chaque fenêtre
        user_id = str(i)
        try:
            page.click("#tournaments")
            print(f"✔️ Fenêtre {i} : Clic sur user #{user_id}")
        except:
            print(f"❌ Fenêtre {i} : User #{user_id} non trouvé")

        # Enregistrer les objets pour chaque fenêtre
        browsers.append(browser)
        contexts.append(context)
        pages.append(page)

    # Attendre que tous les éléments de tournoi soient créés, puis cliquer sur "next-match"
    for i in range(4):
        page = pages[i]  # Utiliser la page spécifique à chaque fenêtre

        try:
            # Attente explicite que le bouton "next-match" soit visible pour chaque fenêtre
            page.wait_for_selector('div.pattern-match.next-match', state="visible", timeout=5000)
            page.click('div.pattern-match.next-match')
            print(f"✔️ Fenêtre {i+1} : clic sur next-match")
        except Exception as e:
            print(f"❌ Fenêtre {i+1} : next-match non trouvé. Erreur: {e}")

    print("Tous les joueurs ont cliqué sur next-match.")

    input("Appuyez sur Entrée pour fermer les navigateurs...")

    # Fermer tous les navigateurs et contextes
    for context in contexts:
        context.close()
    for browser in browsers:
        browser.close()


with sync_playwright() as playwright:
    run(playwright)