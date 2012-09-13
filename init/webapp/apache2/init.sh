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
    packages|stop|start|virtualhost) eval arg_$p=true;;
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
# Apache2
# -------------
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo a2enmod wsgi
#sudo apt-get install libapache2-mod-fcgid
#sudo a2enmod fcgid
#sudo apt-get install libapache2-mod-python
# -------------
#sudo apt-get install libapache2-mod-auth-cas
#sudo a2enmod auth_cas
# -------------
#sudo a2enmod rewrite
# -------------
#sudo apt-get install openssl
#sudo a2enmod ssl
#sudo a2ensite default-ssl
# -------------

# flask



# Engix
# -------------
# sudo apt-get install nginx
# sudo apt-get install uwsgi
fi


if [ $arg_stop ]; then
echo "\n: stop site"
echo "------------------------------------------"
for avisite in $fdn/sites-available/*;
do
avisite=$(basename $avisite)
sudo a2dissite $avisite
#sudo unlink /etc/apache2/sites-enabled/$avisite
sudo unlink /etc/apache2/sites-available/$avisite
done
sudo service apache2 restart
fi

if [ $arg_start ]; then
echo "\n: start site"
echo "------------------------------------------"
sudo ln -s $fdn/sites-available/* /etc/apache2/sites-available/
sudo a2ensite $project
sudo service apache2 restart
fi



