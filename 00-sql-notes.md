# Outstanding issues

The query is slow.. it can take 0.5sec.

The underlining issue is that... many isbns are related to one another but we have no group of them under one id...

If somone could build a table that links all item\_no to related item\_no.. then we could have one simple 

# SQL for recommendations

NOTE: related ISBNs are group together and displayed. For instance, if a related book _Foo_ has isbns A B C then A B C are each listed as recomendations when only one of the 3 would be interesting.

TODO: select one random ISBN from a group of item\_no isbn\_lookup


    DROP TABLE IF EXISTS baked_recomends;
    CREATE TABLE baked_recomends (
        isbn_lookup character varying(16) NOT NULL,
        isbn character varying(16) NOT NULL,
        poppop int NOT NULL
    );
    --truncate relateditemcache;
    CREATE INDEX backed_recomend_isbn_lookup ON baked_recomends USING btree (isbn_lookup);
    
    insert into baked_recomends (isbn_lookup, isbn, poppop)
    (
    --   SELECT isbn_lookup, item_no, institution, isbn, poppop, rank FROM 
      SELECT isbn_lookup, isbn, poppop FROM 
      (SELECT isbn_lookup, item_no, institution, isbn, poppop, rank() OVER (PARTITION BY isbn_lookup, isbn_lookup ORDER BY poppop, isbn DESC) from
        (SELECT isbn_lookup, itemmmm.item_no, itemmmm.institution, itemmmm.isbn, sum(pop) AS poppop FROM item AS itemmmm,
        -- all transaction items of users 
          (SELECT distinct isbn_lookup, transactionnn.patron_id, transactionnn.item_no, transactionnn.institution, count(*) as pop FROM transaction as transactionnn,
        -- that checked out items
            (select distinct isbn_lookup, transactionn.patron_id, transactionn.institution from transaction as transactionn,
        -- related to item_no(s)
              (select distinct isbn_lookup, ii.item_no, ii,institution from item as ii, 
        -- related to isbn(s)
                (select distinct isbn_lookup, i.isbn from item as i, 
        -- found with items_no
                  (select Theisbn.isbn_lookup, iitme.item_no, iitme.institution from item as iitme,
        -- that have isbn
        
        -- MANUAL ISBN
        --(select '9780321643728'::text as isbn_lookup) as Theisbn
        -- RANDOM ISBN(s)
        -- (select isbn as isbn_lookup from item order by random() limit 10000) as Theisbn
        -- ALL ISBN(s)
                  (select isbn as isbn_lookup from item) as Theisbn
                  
                  where TRUE and iitme.isbn = Theisbn.isbn_lookup ) as ind
                where i.item_no = ind.item_no and i.institution = ind.institution ) as allrelatedisbn
              where ii.isbn = allrelatedisbn.isbn) as relateditemno
            where TRUE and transactionn.item_no = relateditemno.item_no) as usr
            
        --  (select iiittem.item_no, iiittem.institution from item as iiittem where iiittem.isbn = isbn_lookup) as blacklist
          WHERE
        --  NOT transactionnn.item_no = blacklist.item_no
        --  AND transactionnn.institution = blacklist.institution
          NOT EXISTS (
            select iiittem.item_no, iiittem.institution from item as iiittem 
            where iiittem.isbn = isbn_lookup
            and iiittem.item_no = transactionnn.item_no
            and iiittem.institution = transactionnn.institution 
          )
          AND transactionnn.patron_id = usr.patron_id
          AND transactionnn.institution = usr.institution
          GROUP BY isbn_lookup, transactionnn.patron_id, transactionnn.item_no, transactionnn.institution) AS otheruserstookout
        WHERE itemmmm.item_no = otheruserstookout.item_no and itemmmm.institution = otheruserstookout.institution
        GROUP BY isbn_lookup, itemmmm.item_no, itemmmm.institution, itemmmm.isbn
        HAVING sum(pop) > 1
        ORDER BY isbn_lookup, poppop desc, itemmmm.item_no) as resultsss
      WHERE TRUE) as final
      WHERE final.rank < 20
    );
        
    # get all related isbn(s)
    select distinct isbn from item as i, 
    (select item_no from item where TRUE isbn = '0039233677') as ind
    where i.item_no = ind.item_no
    
    # get limited selection of related isbn(s)
    select isbn from item as i, 
    (select item_no from item where TRUE and isbn = '0039233677' 
    order by random() 
    limit 1) as ind
    where i.item_no = ind.item_no
    
    # get related item_no(s) given a isbn (6ms)
    select distinct ii.item_no, ii,institution from item as ii, 
    (select distinct isbn from item as i, 
    (select item_no, institution from item where TRUE and isbn = '0039233677') as ind
    where i.item_no = ind.item_no and i.institution = ind.institution ) as allrelatedisbn
    where ii.isbn = allrelatedisbn.isbn
    
    
    select distinct ii.item_no, ii,institution from item as ii, 
    (select distinct isbn from item as i, 
    (select item_no, institution from item where TRUE and isbn = '0039233677') as ind
    where i.item_no = ind.item_no and i.institution = ind.institution ) as allrelatedisbn
    where ii.isbn = allrelatedisbn.isbn
    
    
    # get users from transaction that checked out the item_no(s) (129ms)
    select distinct transactionn.patron_id, transactionn.institution from transaction as transactionn,
    (select distinct ii.item_no, ii,institution from item as ii, 
    (select distinct isbn from item as i, 
    (select item_no, institution from item where TRUE and isbn = '0039233677') as ind
    where i.item_no = ind.item_no and i.institution = ind.institution ) as allrelatedisbn
    where ii.isbn = allrelatedisbn.isbn) as relateditemno
    where TRUE and transactionn.item_no = relateditemno.item_no
    
    # get all items that the users took out (280ms)
    select distinct transactionnn.patron_id, transactionnn.item_no, transactionnn.institution from transaction as transactionnn,
      (select distinct transactionn.patron_id, transactionn.institution from transaction as transactionn,
        (select distinct ii.item_no, ii,institution from item as ii, 
          (select distinct isbn from item as i, 
            (select item_no, institution from item where TRUE and isbn = '0039233677') as ind
          where i.item_no = ind.item_no and i.institution = ind.institution ) as allrelatedisbn
        where ii.isbn = allrelatedisbn.isbn) as relateditemno
      where TRUE and transactionn.item_no = relateditemno.item_no) as usr
    where transactionnn.patron_id = usr.patron_id and transactionnn.institution = usr.institution
    
    # get list of all isbn(s) linked to item_no (282ms)
    select itemmmm.item_no, itemmmm.isbn, count(*) as pop from item as itemmmm,
    (select distinct transactionnn.patron_id, transactionnn.item_no, transactionnn.institution from transaction as transactionnn,
    (select distinct transactionn.patron_id, transactionn.institution from transaction as transactionn,
    (select distinct ii.item_no, ii,institution from item as ii, 
    (select distinct isbn from item as i, 
    (select item_no, institution from item where TRUE and isbn = '0039233677') as ind
    where i.item_no = ind.item_no and i.institution = ind.institution ) as allrelatedisbn
    where ii.isbn = allrelatedisbn.isbn) as relateditemno
    where TRUE and transactionn.item_no = relateditemno.item_no) as usr
    where transactionnn.patron_id = usr.patron_id and transactionnn.institution = usr.institution) as otheruserstookout
    where itemmmm.item_no = otheruserstookout.item_no and itemmmm.institution = otheruserstookout.institution
    group by itemmmm.item_no, itemmmm.isbn
    order by pop desc
    limit 35
    
    
    # get list of all isbn(s) linked to item_no smarter? (284ms)
    select itemmmm.item_no, itemmmm.isbn, sum(pop) as poppop from item as itemmmm,
    (select distinct transactionnn.patron_id, transactionnn.item_no, transactionnn.institution, count(*) as pop from transaction as transactionnn,
    (select distinct transactionn.patron_id, transactionn.institution from transaction as transactionn,
    (select distinct ii.item_no, ii,institution from item as ii, 
    (select distinct isbn from item as i, 
    (select item_no, institution from item where TRUE and isbn = '9780176501655') as ind
    where i.item_no = ind.item_no and i.institution = ind.institution ) as allrelatedisbn
    where ii.isbn = allrelatedisbn.isbn) as relateditemno
    where TRUE and transactionn.item_no = relateditemno.item_no) as usr
    where transactionnn.patron_id = usr.patron_id and transactionnn.institution = usr.institution
    group by transactionnn.patron_id, transactionnn.item_no, transactionnn.institution
    ) as otheruserstookout,
    (select item_no, institution from item where TRUE and isbn = '9780176501655') as blacklist
    where itemmmm.item_no != blacklist.item_no AND itemmmm.institution != blacklist.institution
    and itemmmm.item_no = otheruserstookout.item_no and itemmmm.institution = otheruserstookout.institution
    group by itemmmm.item_no, itemmmm.isbn
    order by poppop desc
    limit 35
    
    
    -- CREATE related isbn related item_no cache
    truncate related_isbn_item_cache;
    insert into related_isbn_item_cache (isbn, item_no, institution)
    (
    select distinct itembbb.isbn, itembbb.item_no, itembbb.institution from item as itembbb
    (select distinct item_no, institution from item,
      (select isbn from item order by random() desc limit 1) as isbntbl
      join 
    where itembbb.isbn = isbntbl.isbn)
    )
    
    
    
    
               
    -- CREATE related item_no cache ...4.1065807 minutes
    truncate relateditemcache;
    insert into relateditemcache (item_no, institution, linked_item_no, linked_institution) 
    (
    select isbnsrelatedtoitem.item_no, isbnsrelatedtoitem.institution, itemlist.item_no, itemlist.institution from item as itemlist,
      -- get isbns for item
      (select itemtocash.item_no, itemtocash.institution, isbn from item as itemp,
        -- get item num and inst list
        (select itemc.item_no, itemc.institution from item as itemc
        --TEST order by random() desc limit 5000
        ) as itemtocash
      where itemp.item_no = itemtocash.item_no and itemp.institution = itemtocash.institution) as isbnsrelatedtoitem          
    where itemlist.isbn = isbnsrelatedtoitem.isbn
    group by isbnsrelatedtoitem.item_no, isbnsrelatedtoitem.institution, itemlist.item_no, itemlist.institution
    order by isbnsrelatedtoitem.item_no
    )
    
    
    
    
    
    
    -- create table where item_no inst gives related items and isbns (333,568.747 ms)
    truncate relateditemcache2;
    
    create TEMPORARY sequence tmp_relateditemcache2_serial;
    SELECT nextval('tmp_relateditemcache2_serial') as tmpserial;
    
    --insert into relateditemcache2 (item_no, institution, linked_item_no, linked_institution, isbn) (
    -- select extra isbns that relate to the related
    select tmpserial, isbnsrelatedtoitem2.pitem_no, isbnsrelatedtoitem2.pinstitution, itemlist2.item_no, itemlist2.institution, itemlist2.isbn from item as itemlist2,
      
    
      
    -- select isbns from other institution that relate
      (select tmpserial, isbnsrelatedtoitem.item_no as pitem_no, isbnsrelatedtoitem.institution as pinstitution, itemlist.isbn as pisbn from item as itemlist,
      
        (SELECT nextval('tmp_relateditemcache2_serial')) as tmpserial,
      
        -- get isbns for item
        (select itemtocash.item_no, itemtocash.institution, isbn from item as itemp,
          -- get item num and inst list
          (select itemc.item_no, itemc.institution from item as itemc
          -- small test:
          order by random() desc limit 4
          ) as itemtocash
        where itemp.item_no = itemtocash.item_no and itemp.institution = itemtocash.institution) as isbnsrelatedtoitem          
      where itemlist.isbn = isbnsrelatedtoitem.isbn ) as isbnsrelatedtoitem2
      
      where itemlist2.isbn = isbnsrelatedtoitem2.pisbn
      group by tmpserial, isbnsrelatedtoitem2.pitem_no, isbnsrelatedtoitem2.pinstitution, itemlist2.item_no, itemlist2.institution, itemlist2.isbn
    --  order by isbnsrelatedtoitem2.pitem_no
    --)
    
    
    
    
    
    
    
    -- CREATE related isbn related item_no cache
    truncate related_isbn_item_cache;
    insert into related_isbn_item_cache (isbn,item_no, institution)
    (
      select distinct relateditemcache2.isbn, linked_item_no, linked_institution from relateditemcache2, 
      (
        select distinct itemtbl.isbn from item as itemtbl
    --    order by random() desc limit 1
      ) as linkcache
      where linkcache.isbn = relateditemcache2.isbn
    )
    
    -- recomends
    select usersinterestedinbook.isbn, usersinterestedinbook.patron_id FROM transaction as transactionnnx,
    (SELECT distinct itemtbl.isbn, transactionnn.patron_id, transactionnn.item_no, transactionnn.institution FROM transaction as transactionnn, 
    
    (select distinct isbn, item_no, institution from item
    where isbn = '9780176501655') as itemtbl
    
    where transactionnn.item_no = itemtbl.item_no and transactionnn.institution = itemtbl.institution) as usersinterestedinbook
    where transactionnnx.patron_id = usersinterestedinbook.patron_id and transactionnnx.institution = usersinterestedinbook.institution
