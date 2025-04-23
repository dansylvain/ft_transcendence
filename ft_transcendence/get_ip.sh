#!/bin/bash

# Récupérer l'IP locale de la machine hôte
HOST_IP=$(hostname -I | awk '{print $1}')

# Vérifier si HOST_IP existe déjà dans le fichier .env
if grep -q "^HOST_IP=" .env; then
    # Remplacer la ligne existante contenant HOST_IP
    sed -i "s/^HOST_IP=.*/HOST_IP=$HOST_IP:8443/" .env
else
    # Ajouter HOST_IP à la fin du fichier .env
    echo "HOST_IP=$HOST_IP:8443" >> .env
fi