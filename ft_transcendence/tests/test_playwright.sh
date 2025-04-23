#!/bin/bash
source tests/utils.sh

start=$(date +%s)

echo "✅ Serveur prêt, lancement des tests..."
echo "Running Playwright tests..."

python3 tests/test_404.py
sleep 1
python3 tests/test_authentication.py
sleep 1
python3 tests/test_2fa.py
sleep 1
python3 tests/test_cookies.py
sleep 1
python3 tests/test_username.py
sleep 1
python3 tests/test_sametime_auth.py
sleep 1
python3 tests/test_xss_sql.py
sleep 1
python3 tests/test_navigation.py
check_result "Playwright tests"

end=$(date +%s)
elapsed=$((end - start))
echo "⏱️ Tests terminés en $elapsed secondes"