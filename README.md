# SPLURGE: Scholars Portal Library Usage-Based Recommendation Generation Engine

Amazon.ca has a "customers who bought this item also bought" feature that recommends things to you that you might be interested in.  LibraryThing has it too: the recommendations for [What's Bred in the Bone](https://www.librarything.com/work/4872560) by Robertson Davies include books by Margaret Laurence, Carol Shields, Michael Ondaatje, Peter Ackroyd, John Fowles, and David Lodge, as well as other Davies works.

Library catalogues don't have any such feature, but they should. And libraries are sitting on the circulation and usage data that makes it possible.  ([BiblioCommons](http://www.bibliocommons.com/) does have a Similar Titles feature, but it's a closed commercial product aimed at public libraries, and anyway the titles are added by hand.)

SPLURGE will collect usage data from OCUL members and build a recommendation engine that can be integrated into any member's catalogue.  The code will be made available under the GNU Public License and the data will be made available under an open data license.

## Background

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

# Related reading

* ["Readers who borrowed this also borrowed...": Recommender Systems in UK libraries](http://www.emeraldinsight.com/journals.htm?issn=0737-8831&volume=30&issue=1&articleid=17014513&show=abstract), by Simon Wakeling, Paul Clough, Barbara Sen and Lynn Connaway (_Library Hi Tech_ 30:1)

# TO DO

* Use xISBN and thingISBN: given book X, look up other manifestations of the same work, then look for and dedupe recommendations for all of them. Instead of offering recommendations based on one edition of a work, it would offer them based on the work.
* Go beyond ISBNs into other standard numbers, such as LCCN and OCLCnums
* Go beyond standard numbers!
* Use for collection development purposes: give collection librarians a way of looking up what's recommended for a given book and seeing if it's in their collection. (Talk to collection librarians about what exactly they'd want.)

# To start up

    # install and use database from a dump
    sh init.sh pgsql
    
    # if you want to start fresh then you can
    # install database from a schema 
    cd init/database/pgsql/
    sh init.sh install_schema
    
    # now if you started fresh you will need to build the tables... use tool.py
    cd app/splurge
    python tool.py --update_database
    
    # test
    cd app/splurge
    python tool.py --test
    
    # if you got the test to work then good lets start the webapp
    cd webapp
    sh ./start.sh
    # you will now have a webservice runing at
    http://127.0.0.1:5000/
    # here is the service
    http://127.0.0.1:5000/splurge_service
    # here is an example using the service
    http://127.0.0.1:5000/static/index.html
    
    
    # once new data is added to the ftp we can pull it using
    python tool.py --update_csvfiles
    # then update the database using
    python tool.py --update_database
    # this task could be a monthly cron
    

# Test ISBNs

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


