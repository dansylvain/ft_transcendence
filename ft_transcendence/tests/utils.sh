#!/bin/bash

# Couleurs pour le feedback
GREEN="\e[32m"
RED="\e[31m"
RESET="\e[0m"

# Fonction pour afficher le résultat d'un test
function check_result {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✔] $1 passed${RESET}"
    else
        echo -e "${RED}[✘] $1 failed${RESET}"
        exit 1
    fi
}