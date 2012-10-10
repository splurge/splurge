#!/usr/bin/env python

import argparse
parser = argparse.ArgumentParser(description='Process Splurge.')
parser.add_argument('--update_database', action='store_true', help='read all ./data into database tables')
parser.add_argument('--old_update_database', action='store_true', help='read all ./data into database tables')
parser.add_argument('--test', action='store_true')
args = parser.parse_args()

import os
root_app_path = os.path.join(os.path.dirname(__file__), 'app/')
root_app_bin_path = os.path.join(root_app_path, 'bin/')
import sys
sys.path.append(root_app_bin_path) 
import splurge

splurge = splurge.Splurge(
    os.path.join(root_app_path, 'data/'),
    os.path.join(root_app_path, 'logs/'),
    'splurge', 'splurge_user', os.environ['SPLURGE_DB_PASSWORD'], 'localhost', '5432',
)

if args.update_database: splurge.load_institution_updates()
if args.old_update_database: splurge.old_update_database()

if args.test:
  # Show recommendations for a random isbn(None) from Institution york between the years ...
  # splurge.test2(None, splurge.createTransactionFilter(splurge.getInstitutionId('york'),'1985','2014') )
  # Other possibilities:
  # splurge.test2('9781552211281', splurge.createTransactionFilter(splurge.getInstitutionId('waterloo')) )
  # splurge.test2('9781552211281')
  # Random ISBN test
  for i in range(4):
    splurge.test()
