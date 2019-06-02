import sqlite3 as sql
import sys
import cgi
import json
from flask import Flask, jsonify
app = Flask(__name__)
print("worked")

sys.stdout.write("Content-Type: application/json")
sys.stdout.write("\n")
sys.stdout.write("\n")

form = cgi.FieldStorage()
print("worked")
#sys.stdout.write(json.dumps({ 'data': form.getvalue('ac_number')}))

with sql.connect('coursesys.db') as db:
    c = db.cursor()
addTeam = """UPDATE Capstone_Team_Members
             SET Team_Number = ?
             WHERE student_email = ?"""
# c.execute(addTeam, (number[0],number[1]))