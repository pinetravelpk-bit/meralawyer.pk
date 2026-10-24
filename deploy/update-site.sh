#!/usr/bin/env bash
# Run on the VPS to pull the latest site from GitHub.
#   ssh root@72.62.193.221 'bash /var/www/meralawyer/deploy/update-site.sh'
set -euo pipefail
cd /var/www/meralawyer
git fetch --quiet origin main
git reset --hard --quiet origin/main
chown -R www-data:www-data /var/www/meralawyer
echo "Deployed $(git log -1 --format='%h %s')"
