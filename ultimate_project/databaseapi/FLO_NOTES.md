✅
⛔
🟧
⚠️
--------------------------------------------------------------------------------
									LAST DEV WEEK
--------------------------------------------------------------------------------

✅ Create a worklofo to delete the DB at 42

✅ Test and stabilize multi-users connection (once everything is locked up) 

🟧 Beautify register / login / 2fa landing pages

🟧 Find a way to lock the database routes as well

🟧✅ Lock all the routes (lock les routes visibles dans le front)

🟧 DELETE ALL THE PRINT OF DEBUG WITH SENSITIVE INFOS

🟧 VOIR LE REGEX DE SEB DANS DISCORD POUR SES WEBSOCKETS (lock )

🟧 DELETE THIS FILE

🟧 DELETE ALL SENSITIVE FILES ON RASPBERRY ENDPOINT, ECT...

🟧 XSS / Injection SQL sur tout les formulaires

🟧 Changer le mot de passe d'admin / Delete l'admin en production

🟧 Garder des users standarts pour la correction

🟧 https://docs.djangoproject.com/en/5.1/ref/csrf/#csrf-limitations
==> Proteger les routes de POST / PUT / DELETE avec des decorateurs CSRF adequats

🟧 Mettre un decorateur sur l'API gateway ?

🟧 Encoder les clefs SSL de NGINX ?

🟧 Mettre un bouton retour HOME sur les pages d'erreur (maxi casse couilles)

🟧 Implementer les pages d'erreur si pas auth a la fin de la semaine







--------------------------------------------------------------------------------
									TOUDOU
--------------------------------------------------------------------------------


🟧 DELETE LE BASH MIGRATION.DELETE.SH DANS LE MAKEFILE

🟧 LIMITER LA LENGHT DES INPUTS DANS LES FORMULAIRES ==> VOIR AVEC MERGE THOMAS

🟧 Retravailler la securisation des routes dans fastAPI

✅ TODO FOR DELETING THE DATABASE

✅ METTRE LES CHAMPS REQUIRED DANS DELETE-PROFILE.HTMl sur les champs password et otp

✅ Tester le multi login sur la branche `prevent_double_auth`

✅ TESTER LE WORKLOW : Register -> turn on 2FA -> Logout -> Login -> 2FA -> Disable 2fa -> Logout -> Login -> delete user -> Login

✅ CREER DES TEST AVEC LE CSRF TOKEN	

✅ FIX LES TEST DES 2FA QUI PLANTES PARFOIS dans playright


`STABILIZATION`:

## BASE REQUIREMENTS

✅ Bouton Back and Forward (notaament dans un match)
✅ Pong contre soi-meme
✅ Tournoi 
✅ Mettre des alias a chaque debut de tournoi
🟧 Injections SQL / XSS
✅ HTTPS (wss)
🟧 Secure routes API
🟧
✅

`AVATAR CREATION` :

In user creation : create a default image when creating an user




⛔ ✅  
## DONE OF THE DAY
✅  Simplifies the django admin panel credentials 


## TO DO LATER
⛔ ✅  Split `admin` id from the `Players` logic to avoid getting disconnected (complicated, if we can avoid it is good )

⛔ ✅ La route `http://localhost:8000/login/` fonctionne, mais la route `http://localhost:8000/login` (check ngninx or fastAPI shit) 


# PRIORITY

⛔ ✅  Strip every useless requirements logics from `user`, `authentication` and `database-api`


## JWT :

✅ Create a very specific login and register route free of JWT requirements
⛔ ✅ Transfert the ping logic from a `curl` command to let the `auth` container handle the logic
⛔ ✅
⛔ ✅
⛔ ✅

⛔ ✅ Connect the form for login in the first place WITHOUT 2FA
⛔ ✅ Create a first version of a JWT.
⛔ ✅ Then displays the token on the front with a redirection






⛔ ✅  Possibly leverage django filters


⛔ ✅ centraliser la documentation django / database / container

--------------------------------------------------------------------------------
									MY ROUTES
--------------------------------------------------------------------------------

http://localhost:8000/admin/  ==>  ADMIN PANEL



--------------------------------------------------------------------------------
									DATABASE ENDPOINTS
--------------------------------------------------------------------------------

```python

# requirements
django-cors-headers




INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    ...
    'corsheaders.middleware.CorsMiddleware',  # This must be BEFORE CommonMiddleware
    'django.middleware.common.CommonMiddleware',
    ...
]

# CORS CONFIGURATION
CORS_ALLOW_CREDENTIALS = True  # 🔥 Allow cookies in requests
CORS_ALLOW_ORIGINS = [
    "http://localhost:8000",  # Basic
    "http://localhost:8001",  # Tournament
    "http://localhost:8002",  # Match
    "http://localhost:8003",  # Static files
    "http://localhost:8004",  # User
    "http://localhost:8005",  # FastAPI
    "http://localhost:8006",  # Authentication
    "http://localhost:8007",  # DatabaseAPI
    f"https://{HOST_IP}",  # Production
]
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
CORS_ALLOW_HEADERS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
CORS_ALLOW_HEADERS = ["*"]




```


--------------------------------------------------------------------------------
									TO ASK
--------------------------------------------------------------------------------


--------------------------------------------------------------------------------
									WIP
--------------------------------------------------------------------------------

2FA :
- Implement necessary libraries
- Create interface with Google Authenticator with big ass QR Code
- Make 2FA optional during registering to website (possibily enable it later ?)
- Create a one time password interface when login-in.
- Store + encrypt securely codes ==> `cryptography` module
- LogOut users on 2FA failure.


--------------------------------------------------------------------------------
									TOUDOU LIST
--------------------------------------------------------------------------------
# TO FIX LATER :
⛔ Health tests visible on the console, maybe put them in  `> /dev/null`

⛔ When refreshing AUTH forms, there is a CSRF verification failed.
When


# 🪡🪡🪡        WORK NEEDLE        🪡🪡🪡🪡🪡🪡



--------------------------------------------------------------------------------
								TO SEARCH  // DOC
--------------------------------------------------------------------------------
- Django Password Hashers : https://docs.djangoproject.com/fr/2.2/topics/auth/passwords/


--------------------------------------------------------------------------------
								DONE STUFF
--------------------------------------------------------------------------------

📅  ===== 26-02 =====

- ✅ DB containers actually create folders of the same service name
- ✅ Potentially shell scripting Automate `makemigrations` on each new app created (no need)

- ✅ Create bind mounts on a a single folder which contains all sub folder related to every database
- ✅ Create multiple postgres containers with a related docker-compose
- ✅ Create SIMPLE models without foreigns keys + Migrate + modify + delete them inside the Djangos apps
- ✅ Connect every containers which contains models to every others dbs
- ✅ Connect each database to the host on a different port, but keep the same port for the docker network

ONE CONTAINER CONNECTING TO MULTIPLE DATABASES
- ✅ Connect `user` to both `user_db` and `match_db` in `user.settings.py`
- ✅ Create a Model in User with a Foreign key
- ✅ Create A few data for `match_db`
- ✅ Create data in `user_db` fetching data from `match_db`

For data simplicity manipulation
- ✅ Connect Django Admin to all DBs


# PRIORITY :
- ✅ Create a dummy model + Connect A regular container to the DB
- ✅ Make Django Admin connect to the db and write in it (double check with SQL queries straight in the container)
- ✅ Connect another container with another models
- ✅ Connect another model to the DB, and with Django Admin again


Write basic doc about databases
Clean Repo from database trying
 Fix health test for postgres

📅  ===== 05-03 =====

✅Recheck les BDD avec dbshell dans chaque container
✅ Deplacer les database de /home/ vers racine
✅ Migrer la logique des dockerfiles + la structure global du compose


📅  ===== 06-03 =====

# Migrating models inside a single container
✅  Create a database_api service
✅  Move the managed models in this one
✅  Delete all the others models
✅  Simplify the models ( maybe already simplified )
✅  Remove the healthchecks for old containers
✅  Create the service database_api
✅  Remove the postgres clients from others containers
✅  Roll back to dummy config like
✅  Remove Admin apps in `INSTALLED_APPS`
✅  Remove Database MiddleWares
✅  Remove anything Database Related
✅  Simplify the SQL schemas to have none


📅  ===== 07-03 =====
✅  Optimize `entrypoint.sh` for  `database_api`
✅  Start making endpoints

📅  ===== 18-03 =====


✅ Create a user `two_fa_app` django_app

✅ Make a route with simple HTML rendering with SPA

✅ SetUp 2FA => Render QR Code + Validation
✅ Once validated the timestamp code => Write in models the key

✅ Then check within the models if data has been correctly wrote

✅ Turn the SetUp2FA button is the user has not enable

✅ Create Disable 2FA is the user has it enabled