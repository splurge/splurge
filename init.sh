#!/bin/sh
frl="$(readlink -f $0)"
fdn="$(dirname $frl)"
fn="$(basename $frl)"
fnb="${fn%.*}"
fnbb="${fn%%.*}"
fnxx="${fn##*.}"

whoami=$(whoami)
hostname=$(hostname -f)
#project=$(basename $fdn)

project=splurge

echo "\n:running as $whoami in path $fdn on system $hostname"
echo "============================================================================================="

for p in $@;
do
  case "$p" in
    rootfs|unlink|link|acl|packages|pgsql|mysql|apache2|nginx) eval arg_$p=true;;
    production)
      arg_force=true;
      arg_link=true;;
    dumpdb)
      sh $fdn/init/database/mysql/init.sh backup;
      sh $fdn/init/database/pgsql/init.sh backup;;
    blankdb)
      sh $fdn/init/database/mysql/init.sh drop create grant;
      sh $fdn/init/database/pgsql/init.sh drop create grant;;
    install)
      arg_packages=true;
      arg_rootfs=true;
      arg_unlink=true;
      arg_link=true;
      arg_acl=true;
      arg_pgsql=true;
      #arg_mysql=true;
      arg_apache2=true;;
    *) echo 'BAD ARGS'; exit 1;;
  esac
done

if [ $arg_packages ]; then
echo "\n: install packages"
echo "------------------------------------------"
sudo apt-get install python-flask
sudo apt-get install python-sqlalchemy
fi

if [ $arg_rootfs ]; then
echo "\n: setup root dev dir"
echo "------------------------------------------"
#sudo mkdir -p /libdev
#sudo chmod g+s /libdev
#sudo chown $whoami:$whoami /libdev
#sudo mkdir -p /libdev/www/
#sudo chown $whoami:$whoami /libdev/www
sudo usermod -a -G www-data $whoami
sudo usermod -a -G $whoami www-data
fi

if [ $arg_unlink ]; then
echo "\n: unlink $project"
echo "------------------------------------------"
sudo unlink /var/www/$project
fi

if [ $arg_link ]; then
echo "\n: link $project"
echo "------------------------------------------"
sudo ln -s $fdn/app/splurge/webapp /var/www/$project
fi

if [ $arg_acl ]; then
echo "/n: set user and file permissions"
echo "---------------------------------"
#sudo chown -R $whoami:$whoami /libweb/www
sudo usermod -a -G www-data $whoami
sudo usermod -a -G $whoami www-data
fi

if [ $arg_mysql ]; then
sh $fdn/init/database/mysql/init.sh install
fi
if [ $arg_pgsql ]; then
sh $fdn/init/database/pgsql/init.sh install
fi
if [ $arg_apache2 ]; then
sh $fdn/init/webapp/apache2/init.sh install
fi
if [ $arg_nginx ]; then
sh $fdn/init/webapp/nginx/init.sh install
fi


