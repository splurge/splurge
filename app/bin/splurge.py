#!/usr/bin/env python

# You must set the environment variable SPLURGE_PASSWORD before running anything.
# It is the Postgres password for user splurge_user.
# In the examples it is splurge, so run this, for example, at a bash shell:
# $ export SPLURGE_PASSWORD=splurge

"""
# TODO: Make SQL injection safe!
# TODO: support mysql and postgres
"""

#import csv
#csv.field_size_limit(1000000000)

import re
import os
import psycopg2
import datetime
import time

class Splurge:
  reIsbn = re.compile(r'''^([0-9]{13}|[0-9xX]{10})$''')
  conn = None
  cur = None
  data_path = None
  log_path = None
  
  reTmp = re.compile('^.*tmp.*$')
  reItem = re.compile('^.*items.*$')
  reTransactions = re.compile('^.*transactions.*$')
  
  def __init__(self, data_path, log_path, database, username, password, hostname, port):
    self.data_path = data_path
    self.log_path = log_path
    #self.constr = "dbname='%s' user='%s' password='%s' host='localhost' port=''" % (database, username, password)
    self.constr = "dbname='%s' user='%s' password='%s' host='%s' port='%s'" % (database, username, password, hostname, port)
    self.db_reconnect()
    
  def db_reconnect(self):
    try:
      if(self.conn):
        self.conn.close()
      self.conn = psycopg2.connect(self.constr)
      self.cur = self.conn.cursor()
    except Exception as e:
      print(e)
      print("ERROR: unable to connect to database")

  def __del__(self):
    if(self.conn):
      self.conn.close()
    
  def addInstitution(self,institution, version = None):
    self.conn.rollback()
    self.cur.execute("insert into institution (institution, version) values (%s, %s);", (institution,version,))
    self.conn.commit()
  def getInstitutions(self):
    self.conn.rollback()
    self.cur.execute("select * from institution")
    return self.cur.fetchall()
  def getInstitution_version(self,institution):
    self.conn.rollback()
    self.cur.execute("select version from institution where institution = %s;", (institution,))
    records = self.cur.fetchall()
    if records: 
        return records[0][0]
    return None
  def updateInstitution_version(self,institution, version):
    self.conn.rollback()
    self.cur.execute("update institution set version = %s where institution = %s;", (version,institution,))
    self.conn.commit()
  def getInstitutionId(self,institution):
    self.conn.rollback()
    self.cur.execute("select institution_id from institution where institution = %s;", (institution,))
    records = self.cur.fetchall()
    if records: 
        return records[0][0]
    return None
  def getItems(self):
    self.conn.rollback()
    self.cur.execute("select * from item")
    return self.cur.fetchall()
  def getTransactions(self):
    self.conn.rollback()
    self.cur.execute("select * from transaction")
    return self.cur.fetchall()
  
  """ get the institutionId, if none found create one """
  def getInstitutionId_or_create(self,institution):
    records = self.getInstitutionId(institution)
    if records: return records
    self.addInstitution(institution)
    records = self.getInstitutionId(institution)
    return records


  """
    itemId (integer)
    ISBN   (string)
    
    file format:
    114784	0415972531
  """
  def load_items_fromfile(self, institution, file):
    institutionId = self.getInstitutionId_or_create(institution)
    print(str(institutionId)+':'+institution + '\t' + file)
    try:
      self.cur.copy_from(open(file,'r'), 'item', sep='\t', columns=('item_no', 'isbn'))
      self.conn.commit()
      self.cur.execute("update item set institution = %s where institution = NULL", (institutionId,))
      self.conn.commit()
    except Exception as e:
      print(str(e))
      log = open(os.path.join(self.log_path, institution+'_'+os.path.basename(file)), 'w')
      log.write('\n'+str(e))
      self.conn.rollback()
      
  """
    timestamp (integer)
    itemId    (integer)
    userId    (integer)
    
    file format:
    1222646400	114784	67890
  """
  def load_transactions_fromfile(self, institution, file):
    institutionId = self.getInstitutionId_or_create(institution)
    print(str(institutionId)+':'+institution + '\t' + file)
    try:
      self.cur.copy_from(open(file,'r'), 'transaction', sep='\t', columns=('transact_time', 'item_no', 'patron_id'))
      self.conn.commit()
      self.cur.execute("update transaction set institution = %s where institution = NULL", (institutionId,))
      self.conn.commit()
    except Exception as e:
      print(str(e))
      log = open(os.path.join(self.log_path, institution+'_'+os.path.basename(file)), 'w')
      log.write('\n'+str(e))
      self.conn.rollback()

  """
    splurge.scholarsportal.info/[institution]/[tmp|now_unix_timestamp]/items.txt
    splurge.scholarsportal.info/[institution]/[tmp|now_unix_timestamp]/transactions.txt

* institution is to be in lower case.
* tmp holds partially uploaded files until all files are ready to be under a timestamp.
* now\_unix\_timestamp is your current timestamp in unix format. 
  """
  def load_institution_updates(self):
    print('\nUpdating database with new data from institutions...\n')
    for institution in os.listdir(self.data_path):
      institution_path = os.path.join(self.data_path, institution)
      if os.path.isdir(institution_path):
        print("\nChecking %s for updates" % (institution,))
        self.getInstitutionId_or_create(institution)
        sorted_timestamps = sorted( [d for d in os.listdir(institution_path)
           if os.path.isdir(os.path.join(institution_path, d)) 
           and not re.match(self.reTmp, d)])
        for timestamp in sorted_timestamps:
            current_institution_version = self.getInstitution_version(institution)
            #fixed format
            #ts = datetime.datetime.strptime( timestamp, "%Y-%m-%dT%H:%M:%S" )
            ts = datetime.datetime.strptime( timestamp, "%Y-%m-%d" )
            #import dateutil.parser
            #ts = dateutil.parser.parse(timestamp)
            if current_institution_version == None or ts.date() > current_institution_version.date():
                print("* Found update: timestamp:%s is < version:%s" % (ts.date(),current_institution_version,))
                institution_update_path = os.path.join(institution_path, timestamp)
                data_files = sorted([f for f in os.listdir(institution_update_path) if os.path.isfile(os.path.join(institution_update_path, f))])
                for data_file in data_files:
                    file = os.path.join(institution_update_path, data_file)
                    if re.match(self.reItem, file):
                        self.load_items_fromfile(institution, file)                   
                    if re.match(self.reTransactions, file):
                        self.load_transactions_fromfile(institution, file)
                ## update timestamp
                self.updateInstitution_version(institution, ts)
                    
  
  # OLD tsv format
  def old_load_isbns_fromfile(self, institution, file):
    institutionId = self.getInstitutionId_or_create(institution)
    print(institution + '\t' + file)
    log = open(os.path.join(self.log_path,os.path.basename(file)), 'w')
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
            self.cur.execute("insert into item (item_no, isbn, institution) values (%s,%s,%s);", (vals))
            self.conn.commit()
          except Exception as e:
            log.write('\n'+str(e))
            self.conn.rollback()
            continue
    except Exception as e:
      log.write('\nERROR:\n' + str(e) + '\n')
      if row: log.write('Row before error:\n' + str(row) + '\n')
  # OLD tsv format
  def old_load_transactions_fromfile(self,institution, file):
    institutionId = self.getInstitutionId_or_create(institution)
    print(institution + '\t' + file)
    log = open(os.path.join(self.log_path,os.path.basename(file)), 'w')
    for line in open(file,'r'):
      vals = list(line.rstrip().split("\t"))
      try:
        self.cur.execute("insert into transaction ( transact_time, item_no, patron_id, institution ) values (to_timestamp(%s),%s,%s,%s);"
          , ( vals[0], vals[1], vals[2], institutionId, ))
        self.conn.commit()
      except Exception as e:
        log.write(str(e) + '\n')
        self.conn.rollback()
        continue  
  
  # OLD METHOD when file name has institution
  def _insert_transactions_fromfile(self,file):
    basename = os.path.basename(file)
    institution = basename.split("-")[0].split("_")[0].split(".")[0]
    self.old_load_transactions_fromfile(institution, file)
  # OLD METHOD when file name has institution
  def _insert_isbns_fromfile(self,file):
    basename = os.path.basename(file)
    institution = basename.split('.')[0].split('-')[0]
    self.old_load_isbns_fromfile(institution, file)
  # OLD !!!!!
  def _update_database_isbns(self):
    print('\nUpdating ISBNs ...\n')
    for filename in os.listdir(self.data_path):
      file = os.path.join(self.data_path, filename)
      if os.path.isfile(file):
        if re.match(self.reItem, file):
          self._insert_isbns_fromfile(file)
  # OLD !!!!!
  def _update_database_transactions(self):
    print('\nUpdating transactions ...\n')
    for filename in os.listdir(self.data_path):
      file = os.path.join(self.data_path, filename)
      if os.path.isfile(file):
        if re.match(self.reTransactions, file):
          self._insert_transactions_fromfile(file)
  # OLD !!!!!
  def old_update_database(self):
    self._update_database_isbns()
    self._update_database_transactions()
    

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
    
  
  def getRandomISBN(self, sqlWhereTransactionFilter=''):
    # NOTE: Grab 100 random transactions because some don't link to an ISBN (might have an import issue on some records)
    # 100 random transactions mitigates the issue.
    # TODO: why do some transactions not have items?
    # TODO: make sql injection safe!
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
  E.g. if a related book foo has ISBNs A B C then A B C are each listed as recommendations when only one of the three would be interesting.
  TODO: speed up query by using a collection of ISBNs that are related to one another.
  TODO: make sql injection safe!
  """
  def getRecommendations(self, isbn=None, sqlWhereTransactionFilter=''):
    if isbn is None: isbn = self.getRandomISBN(sqlWhereTransactionFilter)
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
        isbn = self.getRandomISBN(sqlWhereTransactionFilter)
    print("Recommendations for {0}".format(isbn))
    records = self.getRecommendations(isbn,sqlWhereTransactionFilter)
    for record in records:
        print(record)
      
