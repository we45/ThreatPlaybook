#!/bin/sh
set -ex
echo "VUE_APP_API_URL=$VUE_APP_API_URL" > .env
export VUE_APP_API_URL=$VUE_APP_API_URL
#npm run build
exec "$@"
