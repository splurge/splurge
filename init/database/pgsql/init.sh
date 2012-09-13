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
      arg_grant=true;
      arg_restore=true;;
    install_schema)
      arg_packages=true;
      arg_drop=true;
      arg_create=true;
      arg_grant=true;
      arg_restore_schema=true;;
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
sudo apt-get install postgresql
sudo apt-get install php5-pgsql python-psycopg2
fi

if [ $arg_drop ]; then
echo "\n: drop database $dbname"
echo "------------------------------------------"
sudo -u postgres psql --command "DROP DATABASE $dbname"
fi

if [ $arg_backup ]; then
echo "\n: backup database $dbname"
echo "------------------------------------------"
sudo -u postgres pg_dump $dbname > $fdn/dump.sql
fi

if [ $arg_backup_schema ]; then
echo "\n: backup database schema $dbname"
echo "------------------------------------------"
sudo -u postgres pg_dump --schema-only $dbname > $fdn/schema.sql
fi

if [ $arg_create ]; then
echo "\n: create blank database $dbname"
echo "------------------------------------------"
sudo -u postgres psql --command "CREATE DATABASE $dbname;"
fi

if [ $arg_grant ]; then
echo "\n: grant $dbuser@localhost access to $dbname"
echo "------------------------------------------"
sudo -u postgres psql --command "CREATE ROLE $dbuser LOGIN PASSWORD '$dbpass';"
sudo -u postgres psql --command "GRANT ALL PRIVILEGES ON DATABASE $dbname TO $dbuser;"
# strange but sadly postgress GRANT ALL dont drant to TABLES the SELECT...
#sudo -u postgres psql --command "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $dbuser;"
echo "***********************************************"
echo "database: pgsql://$dbuser:$dbpass@$dbname"
echo "***********************************************"
fi

if [ $arg_restore ]; then
echo "\n: restore database $dbname"
echo "------------------------------------------"
sudo -u postgres psql $dbname < $fdn/dump.sql
fi

if [ $arg_restore_schema ]; then
echo "\n: restore database $dbname"
echo "------------------------------------------"
sudo -u postgres psql $dbname < $fdn/schema.sql
fi


