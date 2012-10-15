#!/usr/bin/env python

# Set the environment variable SPLURGE_PASSWORD before running anything;
# it holds the PostgreSQL password for the database user splurge_user.
# In the examples it is splurge, so run this, for example, at a bash shell:
# $ export SPLURGE_PASSWORD=splurge

"""
# TODO: Make SQL injection safe!
# TODO: support mysql and postgres
"""

import re
import os
import psycopg2
import datetime

class Splurge:
    """
    Class that encapsulates the methods for the SPLURGE recommendation engine
    """
    reIsbn = re.compile(r'''^([0-9]{13}|[0-9xX]{10})$''')
    conn = None
    cur = None
    data_path = None
    log_path = None

    reTmp = re.compile('^.*tmp.*$')
    reItem = re.compile('^.*items.*$')
    reTransactions = re.compile('^.*transactions.*$')
  
    def __init__(self, d_path, l_path, dbase, uname, pwd, host, port):
        self.data_path = d_path
        self.log_path = l_path
        self.constr = "dbname='%s' user='%s' password='%s' host='%s' port='%s'"\
            % (dbase, uname, pwd, host, port)
        self.db_reconnect()
    
    def db_reconnect(self):
        """
        Connect to the database
        """
        try:
            if(self.conn):
                self.conn.close()
            self.conn = psycopg2.connect(self.constr)
            self.cur = self.conn.cursor()
        except Exception as exc:
            print(exc)
            print("ERROR: unable to connect to database")

    def __del__(self):
        """
        Close the database connection on instance clean-up
        """
        if(self.conn):
            self.conn.close()
    
    def add_institution(self, institution, version = None):
        """
        Add an institution to the database
        """
        self.conn.rollback()
        self.cur.execute("""
            INSERT INTO institution (institution, version) VALUES (%s, %s)
        """, (institution, version,))
        self.conn.commit()

    def get_institutions(self):
        """
        Get all institutions from the database
        """
        self.conn.rollback()
        self.cur.execute("""
SELECT institution_id, institution, version FROM institution
        """)
        return self.cur.fetchall()

    def get_inst_ver(self, institution):
        """
        Get the version of a given institution by name
        """
        self.conn.rollback()
        self.cur.execute("""
SELECT version FROM institution WHERE institution = %s
        """, (institution,))
        records = self.cur.fetchall()
        if records: 
            return records[0][0]
        return None

    def update_inst_ver(self, institution, version):
        """
        Update the version of a given institution by name
        """
        self.conn.rollback()
        self.cur.execute("""
UPDATE institution SET version = %s WHERE institution = %s
        """, (version, institution))
        self.conn.commit()

    def get_inst_id(self, institution):
        """
        Get the ID for a given institution by name from the database
        """
        self.conn.rollback()
        self.cur.execute("""
SELECT institution_id FROM institution WHERE institution = %s
        """, (institution,))
        records = self.cur.fetchall()
        if records: 
            return records[0][0]
        return None

    def get_items(self):
        """
        Get all items from the database

        This is probably a bad idea.
        """
        self.conn.rollback()
        self.cur.execute("SELECT * FROM item")
        return self.cur.fetchall()

    def get_transactions(self):
        """
        Get all transactions from the database

        This is probably a bad idea.
        """
        self.conn.rollback()
        self.cur.execute("SELECT * FROM transaction")
        return self.cur.fetchall()
  
    def get_inst_id_or_create(self, institution):
        "Get the inst_id; if none found, create one"
        records = self.get_inst_id(institution)
        if records:
            return records
        self.add_institution(institution)
        records = self.get_inst_id(institution)
        return records


    def load_items_fromfile(self, inst, load_file):
        """
        Loads items from a tab-delimited file.

        The columns are: 
          * itemId (integer)
          * ISBN   (string)
        
        File format:
        114784  0415972531
        """

        inst_id = self.get_inst_id_or_create(inst)
        print(str(inst_id)+':'+inst + '\t' + load_file)
        try:
            self.cur.copy_from(
                open(load_file,'r'), 'item', sep='\t',
                columns=('item_no', 'isbn')
            )
            self.conn.commit()
            self.cur.execute("""
UPDATE item SET inst = %s WHERE inst = NULL
            """, (inst_id,))
            self.conn.commit()
        except Exception as exc:
            print(str(exc))
            inst_name = inst + '_' + os.path.basename(load_file)
            log = open(os.path.join(self.log_path, inst_name), 'w')
            log.write('\n'+str(exc))
            self.conn.rollback()
          
    def load_transactions_fromfile(self, institution, load_file):
        """
        Loads transactions from a tab-delimited file.

        The columns are:
          * timestamp (integer)
          * itemId    (integer)
          * userId    (integer)
        
        File format:
        1222646400	114784	67890
        """

        inst_id = self.get_inst_id_or_create(institution)
        print(str(inst_id)+':'+institution + '\t' + load_file)
        try:
            self.cur.copy_from(
                open(load_file,'r'), 'transaction', sep='\t',
                columns=('transact_time', 'item_no', 'patron_id')
            )
            self.conn.commit()
            self.cur.execute("""
UPDATE transaction SET institution = %s WHERE institution = NULL
            """, (inst_id,))
            self.conn.commit()
        except Exception as exc:
            print(str(exc))
            fname = institution + '_' + os.path.basename(load_file)
            log = open(os.path.join(self.log_path, fname), 'w')
            log.write('\n'+str(exc))
            self.conn.rollback()

    def load_institution_updates(self):
        """
        Loads two files per institution, with the following naming conventions:

        splurge.scholarsportal.info/[institution]/[tmp|now_unix_timestamp]/items.txt
        splurge.scholarsportal.info/[institution]/[tmp|now_unix_timestamp]/transactions.txt

        Notes:
          * institution is to be in lower case.
          * tmp holds partially uploaded files until all files are ready to be under a timestamp.
          * now\_unix\_timestamp is your current timestamp in unix format. 
        """

        print('\nUpdating database with new data from institutions...\n')
        for inst in os.listdir(self.data_path):
            inst_path = os.path.join(self.data_path, inst)
            if os.path.isdir(inst_path):
                print("\nChecking %s for updates" % (inst,))
                self.get_inst_id_or_create(inst)
                sorted_timestamps = sorted([
                    d for d in os.listdir(inst_path)
                    if os.path.isdir(os.path.join(inst_path, d)) 
                    and not re.match(self.reTmp, d)
                ])
                for timestamp in sorted_timestamps:
                    curr_ver = self.get_inst_ver(inst)
                    #fixed format
                    stamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d")
                    if curr_ver == None or stamp.date() > curr_ver.date():
                        print("* Found update: timestamp:%s is < version:%s"
                            % (stamp.date(), curr_ver,)
                        )
                        inst_up_path = os.path.join(inst_path, timestamp)
                        data_files = sorted([
                            f for f in os.listdir(inst_up_path)
                            if os.path.isfile(os.path.join(inst_up_path, f))
                        ])
                        for data_file in data_files:
                            load_file = os.path.join(inst_up_path, data_file)
                            if re.match(self.reItem, load_file):
                                self.load_items_fromfile(inst, load_file)
                            if re.match(self.reTransactions, load_file):
                                self.load_transactions_fromfile(inst, load_file)
                        ## update timestamp
                        self.update_inst_ver(inst, stamp)
  
    def old_load_isbns_fromfile(self, institution, load_file):
        """OLD tsv format"""
        inst_id = self.get_inst_id_or_create(institution)
        print(institution + '\t' + load_file)
        log_file = os.path.join(self.log_path, os.path.basename(load_file))
        log = open(log_file, 'w')
        row = None
        try:
            for line in open(load_file,'r'):
                row = list(line.rstrip().split("\t"))
                nums = row[1].replace('-','').strip('|').split('|')
                for num in nums:
                    # remove char (:pl. from isbn
                    num = re.sub(r"[\(\:pl\.]", "", num)
                    # log isbns with errors
                    if not re.match(self.reIsbn, num):
                        row[1] = num
                        log.write('\nINVALID ISBN: ' + str(row) + '\n')
                        continue            
                    # update database
                    vals = [row[0], num, inst_id]
                    try:
                        self.cur.execute("""
INSERT INTO item (item_no, isbn, institution) VALUES (%s, %s, %s)
                        """, (vals))
                        self.conn.commit()
                    except Exception as exc:
                        log.write('\n'+str(exc))
                        self.conn.rollback()
                        continue
        except Exception as exc:
            log.write('\nERROR:\n' + str(exc) + '\n')
            if row:
                log.write('Row before error:\n' + str(row) + '\n')

    def old_load_transactions_fromfile(self, institution, load_file):
        "Old TSV format"
        inst_id = self.get_inst_id_or_create(institution)
        print(institution + '\t' + load_file)
        log_file = os.path.join(self.log_path, os.path.basename(load_file))
        log = open(log_file, 'w')
        for line in open(load_file,'r'):
            vals = list(line.rstrip().split("\t"))
            try:
                self.cur.execute("""
INSERT INTO transaction ( transact_time, item_no, patron_id, institution )
VALUES (TO_TIMESTAMP(%s), %s, %s, %s)
                """, ( vals[0], vals[1], vals[2], inst_id, ))
                self.conn.commit()
            except Exception as exc:
                log.write(str(exc) + '\n')
                self.conn.rollback()
                continue  

    def _insert_transactions_fromfile(self, load_file):
        "OLD METHOD when file name has institution"
        basename = os.path.basename(load_file)
        institution = basename.split("-")[0].split("_")[0].split(".")[0]
        self.old_load_transactions_fromfile(institution, load_file)

    def _insert_isbns_fromfile(self, load_file):
        "OLD METHOD when file name has institution"
        basename = os.path.basename(load_file)
        institution = basename.split('.')[0].split('-')[0]
        self.old_load_isbns_fromfile(institution, load_file)

    def _update_database_isbns(self):
        "OLD"
        print('\nUpdating ISBNs ...\n')
        for filename in os.listdir(self.data_path):
            load_file = os.path.join(self.data_path, filename)
            if os.path.isfile(load_file):
                if re.match(self.reItem, load_file):
                    self._insert_isbns_fromfile(load_file)

    def _update_database_transactions(self):
        "OLD !!!!!"
        print('\nUpdating transactions ...\n')
        for filename in os.listdir(self.data_path):
            load_file = os.path.join(self.data_path, filename)
            if os.path.isfile(load_file):
                if re.match(self.reTransactions, load_file):
                    self._insert_transactions_fromfile(load_file)

    def old_update_database(self):
        "OLD !!!!!"
        self._update_database_isbns()
        self._update_database_transactions()

    def random_isbn(self, sql_transaction_filter=''):
        """
        Get a random ISBN that matches the user-specified filter

        NOTE: Grab 100 random transactions because some don't link to an ISBN
        (might have an import issue on some records) 100 random transactions mitigates
        the issue.

        TODO: why do some transactions not have items?
        TODO: make sql injection safe!
        """

        self.cur.execute("""
SELECT isbn
FROM item, (
    SELECT item_no, institution
    FROM transaction tf
    WHERE tf.transact_time BETWEEN
        to_timestamp(COALESCE(%(start_year)s, '1900'),'YYYY')
            AND to_timestamp(COALESCE(%(end_year)s, '2999'),'YYYY')
        {0}
    ORDER BY RANDOM()
    LIMIT 100)
AS randomtransaction
WHERE item.item_no = randomtransaction.item_no
    AND item.institution = randomtransaction.institution
LIMIT 1
        """.format(sql_transaction_filter))
        records = self.cur.fetchall()
        return records

    def recommend(self, isbn=None, sql_transaction_filter='', start_year=None,
        end_year=None, max_rank=20
    ):
        """
        Given an ISBN and filter, return recommendations.

        NOTE: related ISBNS are grouped together and displayed.

        For example, if a related book foo has ISBNs A B C, then A B C are each
        listed as recommendations when only one of the three would be
        interesting.

        TODO: speed up query by using a collection of ISBNs that are related to one another.
        TODO: make sql injection safe!
        """

        if isbn is None:
            isbn = self.random_isbn(sql_transaction_filter)
        query = """
WITH recommendations AS (
  SELECT isbn_look, i.isbn, tf.patron_id, tf.item_no, tf.institution, COUNT(*) AS popularity
  FROM transaction tf
        INNER JOIN (
          SELECT isbn AS isbn_look, patron_id, t.institution
          FROM transaction t
            INNER JOIN item i ON t.item_no = i.item_no
          WHERE isbn = %(isbn)s
          GROUP BY isbn_look, patron_id, t.institution
        ) AS usr
          ON tf.patron_id = usr.patron_id
            AND tf.institution = usr.institution
        INNER JOIN item i
          ON tf.item_no = i.item_no
            AND tf.institution = i.institution
        WHERE i.isbn <> %(isbn)s
          {0}
          AND tf.transact_time BETWEEN to_timestamp(COALESCE(%(start_year)s, '1900'),'YYYY')
            AND to_timestamp(COALESCE(%(end_year)s, '2999'),'YYYY')
  GROUP BY isbn_look, i.isbn, tf.patron_id, tf.item_no, tf.institution
  HAVING COUNT(*) > 1
  ORDER BY popularity DESC, isbn_look, tf.item_no
)
SELECT isbn_look::TEXT, isbn::TEXT, popularity::BIGINT FROM (
  SELECT isbn_look, isbn, popularity, RANK() OVER (PARTITION BY isbn_look ORDER BY popularity DESC, isbn) AS rank
  FROM recommendations
) AS final
WHERE final.rank < %(max_rank)s; 
""".format(sql_transaction_filter)
        self.cur.execute(query, {
            'isbn': isbn, 'start_year': start_year, 'end_year': end_year,
            'max_rank': max_rank
        })
        return self.cur.fetchall()
        
    def test(self, isbn=None, sql_transaction_filter=''):
        "Get recommendations for a random ISBN"
        if isbn is None:
            isbn = self.random_isbn(sql_transaction_filter)
        print("Recommendations for {0}".format(isbn))
        records = self.recommend(isbn, sql_transaction_filter)
        for record in records:
            print(record)

def create_transaction_filter(inst_ids=None):
    """ 
    build a sql where filter 
    institutions = CSV list of institution IDs
    """
    #TODO: make sql injection safe!
    wheresql = ""
    if inst_ids: 
        for inst_id in inst_ids:
            if inst_id != None:
                wheresql += " AND tf.institution = {0}".format(inst_id)
    return wheresql
