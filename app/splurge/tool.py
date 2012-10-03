#!/usr/bin/env python

import splurge
import argparse
parser = argparse.ArgumentParser(description='Process Splurge.')
parser.add_argument('--update_csvfiles', action='store_true', help='refresh ./data with ftp data')
parser.add_argument('--update_database', action='store_true', help='read all ./data into database tables')
parser.add_argument('--update_database_isbns', action='store_true', help='read isbns data into database')
parser.add_argument('--update_database_transactions', action='store_true', help='read transactions into database')
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

splurge = splurge.Splurge()
if args.update_csvfiles: splurge.update_csvfiles()
if args.update_database: splurge.update_database()
if args.update_database_isbns: splurge.update_database_isbns()
if args.update_database_transactions: splurge.update_database_transactions()

if args.test:
  # Show recommendations for a random isbn(None) from Institution york between the years ...
  # splurge.test2(None, splurge.createTransactionFilter(splurge.getInstitutionId('york'),'1985','2014') )
  # Other possibilities:
  # splurge.test2('9781552211281', splurge.createTransactionFilter(splurge.getInstitutionId('waterloo')) )
  # splurge.test2('9781552211281')
  # Random ISBN test
  for i in range(4):
    splurge.test()
