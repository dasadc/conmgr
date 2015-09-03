#  source ME

set sourced=($_)
if ("$sourced" == "") then
    echo "Error: source $0"
    exit
endif

set top=$sourced[2]
set dir=`dirname $top`
if ( "$dir" == "." ) then
    set dir=$cwd
endif
    
set path=($dir/{client,server,support} $path)

rehash
