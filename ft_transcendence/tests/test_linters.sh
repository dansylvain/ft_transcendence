#!/bin/bash

source "$(dirname "$0")/utils.sh"

echo "Installing dependencies..."
# pip install --upgrade pip > /dev/null 2>&1
# pip install black flake8 pytest playwright > /dev/null 2>&1
# playwright install > /dev/null 2>&1
check_result "Dependency installation"


echo "Running Black..."
black . --check > /dev/null 2>&1
check_result "Black formatting check"

echo "Running Flake8..."
flake8 . > /dev/null 2>&1
check_result "Flake8 linting"