Here is everything necessary to get SPLURGE running on your own computer.

(As of 1 October 2012: Incomplete.)

# Required packages 

You will need to install (Ubuntu commands in brackets):

* [PostgreSQL](http://www.postgresql.org/) (`sudo apt-get intall postgresql`)
* PostgreSQL development libraries (`sudo apt-get install libpq-dev`)
* [Python](http://www.python.org/) (`sudo apt-get install python`)
* Python development libaries (`sudo apt-get install python-dev`)
* [`pip`](http://pypi.python.org/pypi/pip) (`sudo apt-get install python-pip`)
* [`psycopg2`](http://www.initd.org/psycopg/), Python module for talking to PostgreSQL (`sudo pip install psycopg2`)
* [`flask`](http://flask.pocoo.org/), a simple Python framework for web applications (`sudo pip install flask`)

# Setting up PostgreSQL

First, install it, for example on Ubuntu (see [Ubuntu documentation on PostgreSQL](https://help.ubuntu.com/community/PostgreSQL) for full details, and your own documentation if you use a different operating system)

    $ sudo apt-get install postgresql

Set a password:

    $ sudo -u postgres psql postgres
    postgres=# \password postgres

At the shell, create the splurge_user account and the splurge database:

    $ sudo -u postgres createuser
    Enter name of role to add: splurge_user
    Shall the new role be a superuser? (y/n) n
    Shall the new role be allowed to create databases? (y/n) n
    Shall the new role be allowed to create more new roles? (y/n) n
    $ sudo -u postgres createdb splurge
    $ sudo -u postgres psql
    psql (9.1.5)
    Type "help" for help.
    
    postgres=# alter user splurge_user with encrypted password 'splurge';
    ALTER ROLE
    postgres=# grant all privileges on database splurge to splurge_user;
    GRANT

Note that the password is set to "splurge". For your local testing, this is fine.  In production this should be different.

Now set up the database:

    psql -d splurge -U splurge_user -W < setup.sql 
    
If you get an error like this:

    psql: FATAL:  Peer authentication failed for user "splurge_user"

then follow the instructions at [Get Postgres working on Ubuntu or Linux Mint](http://blog.deliciousrobots.com/2011/12/13/get-postgres-working-on-ubuntu-or-linux-mint/).

# Loading in data

This assumes that you're a developer and have downloaded all of the data files from Scholars Portal into the `app/splurge/data/` directory.

TODO: Add test data to the repo so this works out of the box for non-developers.

Run this:

    $ cd app/splurge
	$ ./tool.py --update_database
    $ ./tool.py --update_database_isbns
	$ ./tool.py --update_database_transactions
	
This will take a while.	

# Running the web service

    $ cd app/splurge/webapp
	$ python splurge_webapp.py

Then go to [http://localhost:3000/static/index.html](http://localhost:3000/static/index.html) and try it out.




