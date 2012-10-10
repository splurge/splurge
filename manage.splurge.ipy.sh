#!/bin/sh
frl="$(readlink -f $0)"
fdn="$(dirname $frl)"
fn="$(basename $frl)"
fnb="${fn%.*}"
fnbb="${fn%%.*}"
fnxx="${fn##*.}"

#sudo apt-get install python
#sudo apt-get install python-dateutil

# use ipython included with manage package

#python $fdn/manage/ipython/ipython.py --no-banner --no-confirm-exit --i --c="%run $fnb $@"
python $fdn/manage/ipython/ipython.py --no-banner --no-confirm-exit --i -- "$fnb" $@

# someday this will work... but need to wait for patches
#sudo apt-get install ipython4??
#ipython4 -i $fnb $@