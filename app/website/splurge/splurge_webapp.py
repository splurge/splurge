#!/usr/bin/env python

import sys
import os

# TODO: perhaps should be using
# Request.environ to access env variables

sys.path.append(os.environ['SPLURGE_ROOT_APP_PATH'] + 'bin/')
import splurge
splurge = splurge.Splurge(
    os.path.join(os.environ['SPLURGE_ROOT_APP_PATH'], 'data/'),
    os.path.join(os.environ['SPLURGE_ROOT_APP_PATH'], 'logs/'),
    'splurge', 'splurge_user', os.environ['SPLURGE_DB_PASSWORD'], 'localhost', '5432',
)

from flask import Flask, jsonify, request
import simplejson as json

app = Flask(__name__)
#app.config.from_pyfile('splurge_production.conf')
app.config.from_pyfile('splurge.conf')

app.debug = True

@app.route("/splurge_service/")
def hello():
    out = """<html><head><title>SPLURGE Help</title></head><body><h1>Welcome to Splurge!</h1>
    <h3>SPLURGE is the Scholars Portal Library Usage-based Recommendation Engine</h3>
    <p><b>URL format:</b> /splurge/&lt;isbn&gt;/&lt;institution&gt/&lt;startYear&gt/&lt;endYear&gt;</p>
    <p>institution startYear and endYear are optional</p>
    
    Example tool:
    http://127.0.0.1:3000/static/index.html
    
    <p>Available institutions:</p>
    <ul>"""
    
    for inst in splurge.getInstitutions():
        out = out + '<li>{0}: {1}</li>'.format(inst[0],inst[1])
    
    out = out + """</ul></body></html>"""
    return out

@app.route("/splurge_service_getinstitutions/", )
def splurge_service_getinstitutions():
    return jsonify(institutions=splurge.getInstitutions());
    
@app.route("/splurge_service/<isbn>/", defaults={'institution_names': None, 'startYear': None, 'endYear': None} )
@app.route("/splurge_service/<isbn>/<institution_names>/<startYear>/<endYear>/", )
def splurge_service(isbn=None, institution_names=None, startYear=None, endYear=None):
    institutions = []
    if institution_names:
        for institution_name in institution_names.split(","):
            institutions.append(splurge.getInstitutionId(institution_name.strip()))
        
    filter = splurge.createTransactionFilter(institutions, startYear, endYear)
    if isbn == None or isbn=='random':
      isbn = splurge.getRandomISBN(filter)
    records = splurge.getRecommendations(isbn, filter)
    return jsonify(isbn=isbn, institution_names=institution_names, institutionIds=institutions, startYear=startYear, endYear=endYear, results=records);

if __name__ == "__main__":
    app.run('0.0.0.0', app.config['SERVER_PORT'])
