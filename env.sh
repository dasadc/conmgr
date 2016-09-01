#  source ME

dir=$(cd $(dirname $BASH_SOURCE); pwd)

PATH=$dir/client:$dir/server:$dir/support:$PATH
