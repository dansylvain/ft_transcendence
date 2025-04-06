#!/bin/bash
source tests/utils.sh

echo "Running Playwright tests..."
python3 tests/test_authentication.py
python3 tests/test_2fa.py
python3 tests/test_cookies.py
python3 tests/test_delete_user.py
python3 tests/test_username.py
python3 tests/test_sametime_auth.py
python3 tests/test_navigation.py
check_result "Playwright tests"

# This container needs to restart to re-create users to be deleted
echo "♻️ Recreating delete users for testing ♻️"
docker restart ctn_databaseapi
echo "✅ Deleted users recreated ✅"