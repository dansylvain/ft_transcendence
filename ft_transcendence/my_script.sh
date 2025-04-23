#!/bin/bash

# Si venv est dispo, on l'utilise. Sinon on passe par virtualenv.
if python3 -m venv env 2>/dev/null; then
    echo "✅ Environnement créé avec venv"
else
    echo "⚠️ venv indisponible, on tente virtualenv"
    pip3 install --user virtualenv
    python3 -m virtualenv env
fi

# Activation de l'environnement
source env/bin/activate

# Installation des dépendances
pip install django black flake8 playwright pyotp

echo "✅ Setup terminé"