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
dbname=${project}
dbuser=${project}
dbpass=qweasd

echo "\n:running as $whoami in path $fdn on system $hostname"
echo "============================================================================================="

for p in $@;
do
  case "$p" in
    packages|drop|create|backup|backup_schema|restore|restore_schema|grant) eval arg_$p=true;;
    production)
      arg_NOTSET=true;;
    install)
      arg_packages=true;
      arg_drop=true;
      arg_create=true;
      arg_restore=true;
      arg_grant=true;;
    install_schema)
      arg_packages=true;
      arg_drop=true;
      arg_create=true;
      arg_restore_schema=true;
      arg_grant=true;;
    install_blank)
      arg_packages=true;
      arg_drop=true;
      arg_create=true;
      arg_grant=true;;
    *) echo 'BAD ARGS..'; exit 1;;
  esac
done

if [ $arg_packages ]; then
echo "\n: install packages"
echo "------------------------------------------"
sudo apt-get install mysql-server
sudo apt-get install php5-mysql python-mysqldb
fi

if [ $arg_drop ]; then
echo "\n: drop database $dbname"
echo "------------------------------------------"
echo "mysql root database password!"
sudo mysql -p -e "DROP DATABASE $dbname;"
fi

if [ $arg_backup ]; then
echo "\n: backup database $dbname"
echo "------------------------------------------"
echo "mysql root database password!"
sudo mysqldump -u root -p $dbname > $fdn/dump.sql
fi

if [ $arg_backup_schema ]; then
echo "\n: backup database schema $dbname"
echo "------------------------------------------"
sudo mysqldump -u root -p --no-data $dbname > $fdn/schema.sql
fi

if [ $arg_create ]; then
echo "\n: create blank database $dbname"
echo "------------------------------------------"
echo "mysql root database password!"
sudo mysql -p -e "CREATE DATABASE $dbname;"
fi

if [ $arg_restore ]; then
echo "\n: restore database $dbname"
echo "------------------------------------------"
echo "mysql root database password!"
sudo mysql -p $dbname < $fdn/dump.sql
fi

if [ $arg_restore_schema ]; then
echo "\n: restore database schema $dbname"
echo "------------------------------------------"
echo "mysql root database password!"
sudo mysql -p $dbname <  $fdn/schema.sql
fi

if [ $arg_grant ]; then
echo "\n: grant $dbuser@localhost access to $dbname"
echo "------------------------------------------"
echo "mysql root database password!"
sudo mysql -p -e "
GRANT USAGE ON $dbname.* TO $dbuser@localhost IDENTIFIED BY '$dbpass';
GRANT ALL ON $dbname.* TO $dbuser@localhost;
FLUSH PRIVILEGES;
"
echo "***********************************************"
echo "database: mysql://$dbuser:$dbpass@$dbname"
echo "***********************************************"
fi
