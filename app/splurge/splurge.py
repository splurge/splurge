#!/usr/bin/env python

"""
# TODO: Make SQL injection safe!
"""

import csv
import re
import os
import psycopg2

class Splurge:

  logPath = os.path.join(os.path.dirname(__file__),"logs/")
  reIsbn = re.compile(r'''^([0-9]{13}|[0-9xX]{10})$''')
  constr = "dbname='splurge' user='splurge_user' host='localhost' password='splurge'"
  conn = None
  cur = None
  
  reItem = re.compile('^.*items.*\.txt$')
  reTransactions = re.compile('^.*transactions.*\.txt$')
  
  def __init__(self):
    csv.field_size_limit(1000000000)
    try:
      self.conn = psycopg2.connect(self.constr)
    except Exception as e:
      print(e)
      print("Unable to connect to database")
      exit()
    self.cur = self.conn.cursor()

  def __del__(self):
    self.conn.close()

  def addInstitution(self,institution):
    #TODO: make sql injection safe!
    self.cur.execute("insert into institution (institution) values ('{0}')".format(institution))
    self.conn.commit()
    
  def getInstitutions(self):
    self.cur.execute("select * from institution")
    return self.cur.fetchall()
    
  def getInstitutionId(self,institution):
    # TODO: Make SQL injection safe!
    self.cur.execute("select institution_id from institution where institution = '{0}'".format(institution))
    records = self.cur.fetchall()
    if records: 
        return records[0][0]
    return None
    
  """ get the institutionId, if none found create one """
  def getInstitutionId_or_create(self,institution):
    records = self.getInstitutionId(institution)
    if records: return records
    self.addInstitution(institution)
    records = self.getInstitutionId(institution)
    return records
  
  def insert_isbns_fromfile(self,file):
    basename = os.path.basename(file)
    institution = basename.split('.')[0].split('-')[0]
    institutionId = self.getInstitutionId(institution)
    print(institution + '\t' + file)
    
    log = open(os.path.join(self.logPath,basename), 'w')
    row = None;
    try:
      for line in open(file,'r'):
        row = list(line.rstrip().split("\t"))
        r = row[1].replace('-','').strip('|').split('|')
        for n in r:
          # remove char (:pl. from isbn
          n = re.sub(r"[\(\:pl\.]", "", n)
          # log isbns with errors
          if not re.match(self.reIsbn, n):
            row[1] = n
            log.write('\nINVALID ISBN: ' + str(row) + '\n')
            continue            
          # update database
          vals = [row[0],n,institutionId]
          try:
            self.cur.execute("insert into item (item_no, isbn, institution) values (%s,%s,%s)", (vals))
            self.conn.commit()
          except Exception as e:
            log.write('\n'+str(e))
            self.conn.rollback()
            continue
    except Exception as e:
      log.write('\nERROR:\n' + str(e) + '\n')
      if row: log.write('Row before error:\n' + str(row) + '\n')
  
  def insert_transactions_fromfile(self,file):
    basename = os.path.basename(file)
    institution = basename.split("-")[0].split("_")[0].split(".")[0]
    institutionId = self.getInstitutionId_or_create(institution)
    print(institution + '\t' + file)
    log = open(os.path.join(self.logPath,basename), 'w')
    
    for line in open(file,'r'):
      vals = list(line.rstrip().split("\t"))
      try:
        self.cur.execute("insert into transaction ( transact_time, item_no, patron_id, institution ) values (to_timestamp(%s),%s,%s,%s)"
          , ( vals[0], vals[1], vals[2], institutionId ))
        self.conn.commit()
      except Exception as e:
        log.write(str(e) + '\n')
        self.conn.rollback()
        continue

  def update_csvfiles(self):
    import os
    os.system('sh data.pull.sh')
    
  def update_database_isbns(self):
    print('\nupdate isbns\n================================')
    path = os.path.join(os.path.dirname(__file__),"data/")
    for filename in os.listdir(path):
      file = os.path.join(path, filename)
      if os.path.isfile(file):
        if re.match(self.reItem, file):
          self.insert_isbns_fromfile(file)

  def update_database_transactions(self):
    print('\nupdate transactions\n================================')
    path = os.path.join(os.path.dirname(__file__),"data/")
    for filename in os.listdir(path):
      file = os.path.join(path, filename)
      if os.path.isfile(file):
        if re.match(self.reTransactions, file):
          self.insert_transactions_fromfile(file)

  def update_database(self):
    self.update_database_isbns()
    self.update_database_transactions()

  ''' 
  build a sql where filter 
  institutions = CSV list of institutionIds
  '''
  def createTransactionFilter(self,institutionIds=None, startYear=None, endYear=None):
    #TODO: make sql injection safe!
    wheresql = ""
    if institutionIds: 
        for institutionId in institutionIds:
            if institutionId != None:
                wheresql += " AND transaction_filterable.institution = {0}".format(institutionId)
    if startYear and endYear: wheresql += " AND transaction_filterable.transact_time between to_timestamp('{0}','YYYY') and to_timestamp('{1}','YYYY')".format(startYear,endYear)
    return wheresql
    
  def getRandomIsbn(self, sqlWhereTransactionFilter=''):
    # NOTE: Grab 100 random transactions because some don't link to an ISBN (must have an import issue on some records)
    # 100 random transactions mitigates the issue.
    # TODO: why do some transactions not have items?
    self.cur.execute("""
    select isbn from item, 
    (select item_no, institution from transaction as transaction_filterable Where true {0} order by random() limit 100) as randomtransaction
    WHERE item.item_no = randomtransaction.item_no AND item.institution = randomtransaction.institution
    limit 1
    """.format(sqlWhereTransactionFilter))
    records = self.cur.fetchall()
    return records
    
  """
  Given an ISBN and filter, return recommendations.
  
  NOTE: related ISBNS are grouped together and displayed.
  Eg if a related book foo has isbns A B C then A B C are each listed as recomendations when only one of the 3 would be interesting 
  TODO: speed up query by using a collection of ISBNs that are related to one another
  """
  def getRecomends(self,isbn=None, sqlWhereTransactionFilter=''):
    if isbn is None: isbn = self.getRandomIsbn(sqlWhereTransactionFilter)
    query = """
SELECT isbn_lookup, isbn, poppop FROM 
  (SELECT isbn_lookup, item_no, institution, isbn, poppop, rank() OVER (PARTITION BY isbn_lookup, isbn_lookup ORDER BY poppop DESC, isbn ) from
    (SELECT isbn_lookup, itemmmm.item_no, itemmmm.institution, itemmmm.isbn, sum(pop) AS poppop FROM item AS itemmmm,
    -- all transaction items of users 
      (SELECT distinct isbn_lookup, transaction_filterable.patron_id, transaction_filterable.item_no, transaction_filterable.institution, count(*) as pop FROM transaction as transaction_filterable,
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
              (select '{1}'::text as isbn_lookup) as Theisbn
              -- RANDOM ISBN(s)
              -- (select isbn as isbn_lookup from item order by random() limit 10000) as Theisbn
              -- ALL ISBN(s)
              -- (select isbn as isbn_lookup from item) as Theisbn
              
              where TRUE and iitme.isbn = Theisbn.isbn_lookup ) as ind
            where i.item_no = ind.item_no and i.institution = ind.institution ) as allrelatedisbn
          where ii.isbn = allrelatedisbn.isbn) as relateditemno
        where TRUE and transactionn.item_no = relateditemno.item_no) as usr
        
    --  (select iiittem.item_no, iiittem.institution from item as iiittem where iiittem.isbn = isbn_lookup) as blacklist
      WHERE
    --  NOT transaction_filterable.item_no = blacklist.item_no
    --  AND transaction_filterable.institution = blacklist.institution
      NOT EXISTS (
        select iiittem.item_no, iiittem.institution from item as iiittem 
        where iiittem.isbn = isbn_lookup
        and iiittem.item_no = transaction_filterable.item_no
        and iiittem.institution = transaction_filterable.institution 
        {0}
      )
      AND transaction_filterable.patron_id = usr.patron_id
      AND transaction_filterable.institution = usr.institution
      {0}
      GROUP BY isbn_lookup, transaction_filterable.patron_id, transaction_filterable.item_no, transaction_filterable.institution) AS otheruserstookout
    WHERE itemmmm.item_no = otheruserstookout.item_no and itemmmm.institution = otheruserstookout.institution
    GROUP BY isbn_lookup, itemmmm.item_no, itemmmm.institution, itemmmm.isbn
    HAVING sum(pop) > 1
    ORDER BY poppop desc, isbn_lookup, itemmmm.item_no) as resultsss
  WHERE TRUE) as final
WHERE final.rank < 20
  """.format(sqlWhereTransactionFilter, isbn)
    self.cur.execute(query)
    return self.cur.fetchall()
    
  def test(self,isbn=None, sqlWhereTransactionFilter=''):
    if isbn is None:
        isbn = self.getRandomIsbn(sqlWhereTransactionFilter)
    print("Recommendations for {0}".format(isbn))
    records = self.getRecomends(isbn,sqlWhereTransactionFilter)
    for record in records:
        print(record)
      
