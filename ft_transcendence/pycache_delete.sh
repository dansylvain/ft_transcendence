#!/bin/bash

# This script is used to delete all "__pycache__" directories and .pyc files in the project.

delete_pycache() {
  for dir in "$1"/*; do
    if [ -d "$dir" ]; then
      if [ "$(basename "$dir")" == "__pycache__" ]; then
        echo "Deleting $dir"
        sudo rm -rf "$dir"
      else
        delete_pycache "$dir"
      fi
    elif [ -f "$dir" ] && [[ "$dir" == *.pyc ]]; then
      echo "Deleting $dir"
      sudo rm -f "$dir"
    fi
  done
}

delete_pycache "$(pwd)"
