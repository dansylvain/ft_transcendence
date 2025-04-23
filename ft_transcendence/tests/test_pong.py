# ! IMPORTANT : For register AND login testing purposes, you need to create a user with the following credentials :
# !  USERNAME : test
# !  EMAIL : test@test.com
# !  PASSWORD : password

# And also another user with the following credentials :
# !  USERNAME : test_2fa
# !  EMAIL : test2@test.com
# !  PASSWORD : password

# ! 2FA USER SECRET : S3EF2KESUQR45MRTL7MXDSJVI6JQDG4R

# from playwright.sync_api import Playwright, sync_playwright

# def run(playwright: Playwright) -> None:
#     base_url = "https://localhost:8443"
#     browsers = []
#     contexts = []
#     pages = []

#     # Positions des fenêtres (2 par ligne)
#     positions = [(0, 0), (800, 0), (0, 600), (800, 600)]

#     urls = [ 
#             f"{base_url}/tournament/simple-match/",
#             f"{base_url}/tournament/tournament/"
#             ]    

#     for i, (x, y) in enumerate(positions):
#         browser = playwright.chromium.launch(
#             headless=False,
#             args=[f"--window-position={x},{y}", "--window-size=800,600"]
#         )
#         context = browser.new_context(ignore_https_errors=True)
#         page = context.new_page()
#         page.set_default_timeout(6000)
#         page.goto(urls[1])
#         page.wait_for_load_state("networkidle")

#         # Seule la première fenêtre clique sur "Create"
#         if i == 0:
#             try:
#                 page.click('button[onclick="newTournament(window.tournamentSocket)"]')
#                 print("✔️ Fenêtre 1 : Bouton 'Create' cliqué")
#             except:
#                 print("❌ Fenêtre 1 : Bouton 'Create' non trouvé")

#         # Chaque fenêtre clique sur son propre élément utilisateur
#         user_id = str(i)  # Chaque joueur a un ID différent
#         try:
#             page.click("#tournaments")
#             print(f"✔️ Fenêtre {i+1} : Clic sur user #{user_id}")
#         except:
#             print(f"❌ Fenêtre {i+1} : User #{user_id} non trouvé")



#         browsers.append(browser)
#         contexts.append(context)
#         pages.append(page)

#     for i in range(4):
#         try:
#             page.wait_for_selector('div.pattern-match.next-match')
#             page.click('div.pattern-match.next-match')
#             print(f"✔️ Fenêtre {i+1} : clic sur next_match")
#         except:
#             print(f"❌ Fenêtre {i+1} : next-match non trouvé")

#     print("Les 4 navigateurs sont ouverts et prêts à l'interaction.")

#     input("Appuyez sur Entrée pour fermer les navigateurs...")

#     for context in contexts:
#         context.close()
#     for browser in browsers:
#         browser.close()

# with sync_playwright() as playwright:
#     run(playwright)


# \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

from playwright.sync_api import Playwright, sync_playwright
import time

# Fonction de navigation avec attente


def navigate(page, url: str):
    page.goto(url)
    page.wait_for_load_state("networkidle")


def run(playwright: Playwright) -> None:
    base_url = "https://localhost:8443"
    browsers = []
    contexts = []
    pages = []

    # ! IMPORTANT : I did not add global pages timeouts for this tests

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
















# def run(playwright: Playwright) -> None:
#     browser = playwright.chromium.launch(headless=False)
#     context = browser.new_context(
    #     ignore_https_errors=True
    # )
#     page = context.new_page()
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/")
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/home/")
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/user/profile/")
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/user/stats/")
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/tournament/simple-match/")
#     time.sleep(0.4)
#     page.locator("#nav-home").click()
#     time.sleep(0.4)
#     page.locator("#nav-tournament").click()
#     time.sleep(0.4)
#     page.locator("#nav-profile").click()
#     time.sleep(0.4)
#     page.locator("#nav-stats").click()
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/home/")
#     page.locator("#field-tournament").click()
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/home/")
#     page.locator("#field-profile").click()
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/home/")
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
#     context = browser.new_context(
        # ignore_https_errors=True
    # )
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

#     page.goto("https://localhost:8443/")
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
#     page.goto("https://localhost:8443/test/")
#     time.sleep(0.4)
#     page.goto("https://localhost:8443/match/")

#     # TEST FLO
#     time.sleep(1)
#     page.goto("https://localhost:8443/user/")
#     time.sleep(1)
#     # TEST FLO
#     websocket_connected = False
#     time.sleep(0.4)

#     def handle_websocket(ws):
#         nonlocal websocket_connected
#         websocket_connected = True
#         print(f"🔌 WebSocket connectée à : {ws.url}")

#     page.on("websocket", handle_websocket)
#     page.goto("https://localhost:8443/match/")
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
