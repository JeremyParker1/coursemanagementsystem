import sqlite3 as sql
from bcrypt import hashpw, gensalt


conn = sql.connect('courseSystem.db')
c = conn.cursor()
# addTeam = """UPDATE Capstone_Team_Members
#                  SET team_number = ?
#                  WHERE student_email=? AND course_id=? AND sec_no=? """
# c.execute(addTeam,(None,"ale8219@lionstate.edu",'CMPSC497',2))
c.execute("""DROP TABLE IF EXISTS Student""")
c.execute("""DROP TABLE IF EXISTS Zipcode""")
c.execute("""DROP TABLE IF EXISTS Professor""")
c.execute("""DROP TABLE IF EXISTS Department""")
c.execute("""DROP TABLE IF EXISTS Course""")
c.execute("""DROP TABLE IF EXISTS Sections""")
c.execute("""DROP TABLE IF EXISTS Enrolls""")
c.execute("""DROP TABLE IF EXISTS Prof_teams""")
c.execute("""DROP TABLE IF EXISTS Prof_team_members""")
c.execute("""DROP TABLE IF EXISTS Homework""")
c.execute("""DROP TABLE IF EXISTS Exams""")
c.execute("""DROP TABLE IF EXISTS Exam_grades""")
c.execute("""DROP TABLE IF EXISTS Homework_grades""")
c.execute("""DROP TABLE IF EXISTS Capstone_section""")
c.execute("""DROP TABLE IF EXISTS Capstone_Team""")
c.execute("""DROP TABLE IF EXISTS Capstone_Team_Members""")
c.execute("""DROP TABLE IF EXISTS Capstone_grades""")
conn.commit()
c.close()