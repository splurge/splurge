# SPLURGE: Scholars Portal Library Usage-Based Recommendation Generation Engine

Amazon.ca has a "customers who bought this item also bought" feature that recommends things to you that you might be interested in.  LibraryThing has it too: the recommendations for [What's Bred in the Bone](https://www.librarything.com/work/4872560) by Robertson Davies include books by Margaret Laurence, Carol Shields, Michael Ondaatje, Peter Ackroyd, John Fowles, and David Lodge, as well as other Davies works.

Library catalogues don't have any such feature, but they should. And libraries are sitting on the circulation and usage data that makes it possible.  ([BiblioCommons](http://www.bibliocommons.com/) does have a Similar Titles feature, but it's a closed commercial product aimed at public libraries, and anyway the titles are added by hand.)

SPLURGE will collect usage data from OCUL members and build a recommendation engine that can be integrated into any member's catalogue.  The code will be made available under the GNU Public License and the data will be made available under an open data license.

# Installation

Here is everything necessary to get SPLURGE running on your own computer.

If you wish to skip creating you databae and webserver you can use the manage.splurge.ipy.sh tool.
Be sure to git clone --recursive to include submodule ipython

Using the manage script for tested on *buntu:

    . ./set_password.sh
    ./manage.splurge.ipy.sh
    app.install()
    https://splurge.localhost/splurge_service/

An other option is to manualy download the packages and configure the services.

(As of 1 October 2012: Incomplete.)

## Required packages 

You will need to install some software packages to use SPLURGE. (Ubuntu commands in brackets.)

* [Git](http://git-scm.com/) for version control (`sudo apt-get install git`)
* [PostgreSQL](http://www.postgresql.org/) (`sudo apt-get intall postgresql`)
* PostgreSQL development libraries (`sudo apt-get install libpq-dev`)
* [Python](http://www.python.org/) (`sudo apt-get install python`)
* Python development libaries (`sudo apt-get install python-dev`)
* [`pip`](http://pypi.python.org/pypi/pip) (`sudo apt-get install python-pip`)
* [`psycopg2`](http://www.initd.org/psycopg/), Python module for talking to PostgreSQL (`sudo pip install psycopg2`)
* [`flask`](http://flask.pocoo.org/), a simple Python framework for web applications (`sudo pip install flask`)

## Setting up PostgreSQL

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

    psql -d splurge -U splurge_user -W < app/db/schema_dump.sql 
    
If you get an error like this:

    psql: FATAL:  Peer authentication failed for user "splurge_user"

then follow the instructions at [Get Postgres working on Ubuntu or Linux Mint](http://blog.deliciousrobots.com/2011/12/13/get-postgres-working-on-ubuntu-or-linux-mint/).

If you ever need to reset the splurge database back to zero and start over, run this command again.

Later, if you want to dump out the database, run

    $     pg_dump -U splurge_user splurge

## Set the SPLURGE_USER environment variable

The password for splurge_user needs to be set in the `SPLURGE_DB_PASSWORD` environment variable before running anything more. (This makes it easier to share code.) Before going on, run this (if you use bash) but, of course, use whatever password you set:

    $ export SPLURGE_DB_PASSWORD=splurge

You could add this line to a login file such as `.bashrc`.

Test that it was set properly by running

    $ echo $SPLURGE_DB_PASSWORD

## Download SPLURGE

Download SPLURGE from the [https://github.com/splurge/splurge.git](https://github.com/splurge/splurge.git):

    $ git clone https://github.com/splurge/splurge.git
    $ cd splurge

## Loading in data

This assumes that you're a developer and have downloaded all of the data files from Scholars Portal into the `app/splurge/data/` directory.

TODO: Add test data to the repo so this works out of the box for non-developers.

Run this:

    $ cd app/splurge
	$ ./tool.py --update_database
	
This will take a while.	

Test it:

	$ ./tool.py --test

## Running the web service

    $ ./tool.py --little_server

Then go to [http://localhost:3000/static/index.html](http://localhost:3000/static/index.html) and try it out.

The service is running at [http://localhost:3000/splurge_service/](http://localhost:3000/splurge_service/)

## Test ISBNs

* 0321643720      
* 9780321643728   
* 0273713248      
* 9780273713241   
* 0763766321      
* 9780763766320   
* 0176501657      
* 9780176501655   
* 9780538733410   
* 9781412974882   
* 0773502424

# TO DO

* Put this under a GPLv2 license (with "or later") (discuss)
* Figure out how best to handle new data uploads, and automate that process so that when new files are uploaded they automatically loaded.
* Use xISBN and thingISBN: given book X, look up other manifestations of the same work, then look for and dedupe recommendations for all of them. Instead of offering recommendations based on one edition of a work, it would offer them based on the work.
* Go beyond ISBNs into other standard numbers, such as LCCN and OCLCnums
* Go beyond standard numbers!
* Use for collection development purposes: give collection librarians a way of looking up what's recommended for a given book and seeing if it's in their collection. (Talk to collection librarians about what exactly they'd want.)

# Background

We plan to implement in Ontario something close to the [JISC](http://www.jisc.ac.uk/) project called [MOSAIC (Making Our Shared Activity Information Count)](http://sero.co.uk/jisc-mosaic-documents.html). The documents there describe what they did, and our plan is based on that.

* [MOSAIC Data Collection: A Guide](http://sero.co.uk/assets/090514%20MOSAIC%20data%20collection%20-%20A%20guide%20v01.pdf)
* [MOSAIC Final Report](http://sero.co.uk/mosaic/100322_MOSAIC_Final_Report_v7_FINAL.pdf) (and [Appendices](http://sero.co.uk/mosaic/100212%20MOSAIC%20Final%20Report%20Appendices%20FINAL.pdf))
* Also [MOSAIC Demonstration Links](http://sero.co.uk/mosaic/091012-MOSAIC-Demonstration-Links.doc), from a software contest they ran to find new, interesting uses for their data. The examples here go beyond 
the Recommendation Engine idea, but are worth looking at to see other 
possible future directions.)

The [JISC MOSAIC wiki](http://library.hud.ac.uk/wikis/mosaic/index.php/Main_Page) has code and data examples.

The JISC project grew out of work done by Dave Pattern (Library Systems Manager) and others at the University of Huddersfield. They made usage data available under an Open Data Commons License.

* [Data](http://library.hud.ac.uk/data/usagedata/)
* [README](http://library.hud.ac.uk/data/usagedata/_readme.html)
* Pattern explains things in [Free book usage data from the University of Huddersfield](http://www.daveyp.com/blog/archives/528)
* Pattern summarized it all in March 2011 in [Sliding Down the Long Tail](http://www.daveyp.com/blog/archives/1453).

Updated 13 Feb: The SALT Recommender API is doing what we want to do, and JISC's planned SALT 2 project is a consortial approach like OCUL would do:

* [SALT Recommender API at Manchester](https://salt11.wordpress.com/salt-recommender-api/)
* [Copac Activity Data Project aka SALT 2](http://copac.ac.uk/innovations/activity-data/)
* [JISC's Activity Data](http://www.activitydata.org/)

Pattern's [Sliding Down the Long Tail](http://www.daveyp.com/blog/archives/1453) describes the logic we'll need to follow.

Tim Spalding implemented a similar feature at [LibraryThing](http://librarything.com/). When asked on Twitter how it worked, he said [The best code is just statistics](https://mobile.twitter.com/librarythingtim/status/126478695828434944) and [Given random distribution how many of book X would you expect? How many did you find?](https://mobile.twitter.com/librarythingtim/status/126480811817046016).

In conversation, both Pattern and Spalding mentioned the _Harry Potter effect_: some books are so popular with everyone that they need to be damped down.  Everyone reading Freud or Ferlinghetti, Feynman or Foucault, is probably also reading J.K. Rowling, but that doesn't mean _Harry Potter and the Goblet of Fire_ should be recommended to people looking at _Totem and Taboo_ or _Madness and Civilization_.

## Related reading

* ["Readers who borrowed this also borrowed...": Recommender Systems in UK libraries](http://www.emeraldinsight.com/journals.htm?issn=0737-8831&volume=30&issue=1&articleid=17014513&show=abstract), by Simon Wakeling, Paul Clough, Barbara Sen and Lynn Connaway (_Library Hi Tech_ 30:1)

