#!/bin/bash
source tests/utils.sh

echo "Running Playwright tests..."
python3 tests/test_authentication.py
sleep 1
python3 tests/test_2fa.py
sleep 1
python3 tests/test_cookies.py
sleep 1
python3 tests/test_delete_user.py
sleep 1
python3 tests/test_username.py
# python3 tests/test_same_time_auth.py #! NOT READY TO SHIP YET
sleep 1
python3 tests/test_navigation.py
check_result "Playwright tests"

# This container needs to restart to re-create users to be deleted
echo "♻️ Recreating delete users for testing ♻️"
docker restart ctn_databaseapi
echo "✅ Deleted users recreated ✅"