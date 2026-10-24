#!/usr/bin/env bash
# Run on the VPS to pull the latest site from GitHub.
#   ssh root@72.62.193.221 'bash /var/www/meralawyer.pk/current/deploy/update-site.sh'
set -euo pipefail
cd /var/www/meralawyer.pk/current
git fetch --quiet origin main
git reset --hard --quiet origin/main
chown -R www-data:www-data /var/www/meralawyer.pk
echo "Deployed $(git log -1 --format='%h %s')"
