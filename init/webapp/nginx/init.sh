#!/bin/sh
frl="$(readlink -f $0)"
fdn="$(dirname $frl)"
fn="$(basename $frl)"
fnb="${fn%.*}"
fnbb="${fn%%.*}"
fnxx="${fn##*.}"

whoami=$(whoami)
hostname=$(hostname -f)

project=splurge

echo "\n:running as $whoami in path $fdn on system $hostname"
echo "============================================================================================="

for p in $@;
do
  case "$p" in
    packages|stop|start) eval arg_$p=true;;
    production)
      arg_NOTSET=true;;
    install)
      arg_packages=true;
      arg_stop=true;
      arg_start=true;;
    *) echo 'BAD ARG'; exit 1;;
  esac
done

if [ $arg_packages ]; then
echo "\n: install packages"
echo "------------------------------------------"
#sudo apt-get install php5-fpm
#sudo aptitude install php5-cli php5-common php5-mysql php5-suhosin php5-gd php5-dev
#sudo aptitude install php5-fpm php5-cgi php-pear php5-memcache php-apc
sudo apt-get install nginx
fi

if [ $arg_stop ]; then
echo "\n: stop site"
echo "------------------------------------------"
for avisite in $fdn/sites-available/*;
do
avisite=$(basename $avisite)
sudo unlink /etc/nginx/sites-enabled/$avisite
sudo unlink /etc/nginx/sites-available/$avisite
done
sudo service nginx reload
fi

if [ $arg_start ]; then
echo "\n: start site"
echo "------------------------------------------"
sudo service apache2 stop
#sudo ln -s $fdn/init/nginx/sites-available/* /etc/nginx/sites-available/
sudo ln -s $fdn/init/nginx/sites-available/* /etc/nginx/sites-enabled/
#sudo service php5-fpm restart
sudo service nginx restart
fi

