#!/bin/sh
#
# launch ADC conmgr app using dev_appserver.py, Google App Engine

DIR=$(dirname $0)
storage_path=${DIR}/../DATA  # デフォルトでは/tmp以下に作られるので、変更する
mkdir ${storage_path}

# proxyの指定があると、なぜか、dev_appserver.pyが動かなくなる。
# HTTPError: HTTP Error 404: Not Found がでる。
unset http_proxy
unset https_proxy
unset ftp_proxy
unset no_proxy
unset HTTP_PROXY
unset HTTP_PROXY_AUTH

dev_appserver.py --host 0.0.0.0 --port 8888 --admin_host 0.0.0.0 --log_level warning --storage_path ${storage_path} ${DIR}
