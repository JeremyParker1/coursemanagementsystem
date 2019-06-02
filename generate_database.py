import csv
import sqlite3 as sql
from bcrypt import hashpw, gensalt

conn = sql.connect('courseSystem.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS Student(email TEXT PRIMARY KEY, password TEXT, name TEXT, age INTEGER,
                                                gender TEXT, major TEXT REFERENCES Department(dept_id),
                                                street TEXT, zipcode INTEGER
                                                REFERENCES Zipcode(zipcode) ON DELETE NO ACTION);""")

c.execute("""CREATE TABLE IF NOT EXISTS Zipcode(zipcode INTEGER PRIMARY KEY, city TEXT, state TEXT);""")

c.execute("""CREATE TABLE IF NOT EXISTS Professor(email TEXT PRIMARY KEY, password TEXT, name TEXT, age INTEGER,
                                                  gender TEXT, office_address TEXT, department TEXT
                                                  REFERENCES Department(dept_id), title TEXT);""")

c.execute("""CREATE TABLE IF NOT EXISTS Department(dept_id TEXT PRIMARY KEY,
                                                    dept_name TEXT,
                                                    dept_head TEXT);""")
c.execute("""SELECT * FROM Department Limit 3 """)
print(c.fetchall())
c.execute("""CREATE TABLE IF NOT EXISTS Course(course_id TEXT PRIMARY KEY, course_name TEXT,
                                               course_description TEXT);""")

c.execute("""CREATE TABLE IF NOT EXISTS Sections(course_id INTEGER REFERENCES Course(course_id) ON DELETE CASCADE,
                                                 sec_no INTEGER, section_type TEXT, limits INTEGER,
                                                 prof_team_id INTEGER REFERENCES Prof_teams(team_id),
                                                 PRIMARY KEY(course_id, sec_no));""")
# TODO: Implement "Limit" Integrity Constraint
c.execute("""CREATE TABLE IF NOT EXISTS Enrolls(student_email TEXT, course_id INTEGER, section_no INTEGER,
                                                  PRIMARY KEY(student_email, course_id));""")
c.execute("""CREATE TABLE IF NOT EXISTS Prof_teams(team_id INTEGER PRIMARY KEY);""")
c.execute("""CREATE TABLE IF NOT EXISTS Prof_team_members(prof_email TEXT,
                                                          team_id INTEGER REFERENCES Prof_teams(team_id),
                                                          PRIMARY KEY(prof_email, team_id));""")
c.execute("""CREATE TABLE IF NOT EXISTS Homework(course_id INTEGER,
                                                 sec_no INTEGER,
                                                 hw_no INTEGER, hw_details TEXT,
                                                 FOREIGN KEY(course_id, sec_no) REFERENCES Sections(course_id, sec_no)
                                                 ON DELETE CASCADE,
                                                 PRIMARY KEY(course_id, sec_no, hw_no)
                                                 );""")
c.execute("""CREATE TABLE IF NOT EXISTS Homework_grades(student_email TEXT REFERENCES Students(email),
                                                        course_id INTEGER REFERENCES Sections(course_id),
                                                        sec_no INTEGER REFERENCES Sections(sec_no),
                                                        hw_no INTEGER, grade REAL,
                                                        FOREIGN KEY(course_id, sec_no) REFERENCES
                                                        Sections(course_id, sec_no) ON DELETE NO ACTION,
                                                        PRIMARY KEY(student_email, course_id, sec_no, hw_no)
                                                        );""")
c.execute("""CREATE TABLE IF NOT EXISTS Exams(course_id INTEGER, sec_no INTEGER, exam_no INTEGER, exam_details TEXT,
                                              PRIMARY KEY(course_id, sec_no, exam_no),
                                              FOREIGN KEY(course_id, sec_no) REFERENCES Sections(course_id, sec_no)
                                              ON DELETE CASCADE
                                              );""")
c.execute("""CREATE TABLE IF NOT EXISTS Exam_grades(student_email TEXT, course_id INTEGER, sec_no INTEGER,
                                                    exam_no INTEGER, grades REAL,
                                                    FOREIGN KEY(course_id, sec_no, exam_no)
                                                    REFERENCES Sections(course_id, sec_no, exam_no) ON DELETE NO ACTION,
                                                    PRIMARY KEY(student_email, course_id, sec_no, exam_no));""")
c.execute("""CREATE TABLE IF NOT EXISTS Capstone_section(course_id INTEGER, sec_no INTEGER, project_no INTEGER,
                                                         sponsor_id INTEGER,
                                                         FOREIGN KEY(course_id, sec_no)
                                                         REFERENCES Sections(course_id, sec_no) ON DELETE CASCADE,
                                                         PRIMARY KEY(course_id, sec_no));""")
c.execute("""CREATE TABLE IF NOT EXISTS Capstone_Team(course_id INTEGER, sec_no INTEGER, team_id INTEGER,
                                                      project_no INTEGER, project_desc TEXT,
                                                      PRIMARY KEY(course_id, sec_no, team_id, project_no));""")
c.execute("""CREATE TABLE IF NOT EXISTS Capstone_Team_Members(student_email TEXT, team_id INTEGER, course_id INTEGER,
                                                              sec_no INTEGER, team_number INTEGER,
                                                              PRIMARY KEY(student_email, team_id, course_id, sec_no
                                                              ));""")
c.execute("""CREATE TABLE IF NOT EXISTS Capstone_grades(course_id INTEGER, sec_no INTEGER, team_id INTEGER,
                                                       team_number INTEGER, grade REAL, project_no INTEGER,
                                                       PRIMARY KEY(course_id, sec_no, team_id, team_number, project_no));""")
with open('Professor.csv', 'r', encoding='UTF8') as profcsv:
    professors1 = list(csv.reader(profcsv, delimiter=','))
    course_prof_team = {}
    capstone_sponsor_dict = {}
    for row in professors1:
         course_prof_team[row[10]] = row[9]
         capstone_sponsor_dict[row[10]] = row[1]

with open('Professor.csv', 'r', encoding='UTF8') as profcsv:
    professors = csv.reader(profcsv, delimiter=',')
    for row in professors:
        c.execute("""INSERT OR IGNORE INTO Professor VALUES (?,?,?,?,?,?,?,?);""", (row[1], hashpw(str.encode(row[2]),
                                                                                    gensalt(4)), row[0], row[3], row[4],
                                                                                    row[6], row[5], row[8]))
        c.execute("""INSERT OR IGNORE INTO Department VALUES (?,?,?);""", (row[5], row[7], row[0]))
        # Row 0 is Dept Head, which is only added to Department if row[5] is unique and new DeptID
        c.execute("""INSERT OR IGNORE INTO Prof_Teams VALUES (?);""", (row[9],))
        c.execute("""INSERT OR IGNORE INTO Prof_team_members VALUES (?,?);""", (row[1], row[9]))
# # TODO: Do we need the comma for row[9],?
# # TODO: Is there no professors on the same team? Should there be?
with open('Student.csv', 'r', encoding='UTF8') as studentcsv:
    students = csv.reader(studentcsv, delimiter=',')
# TODO: name = 1, row[name]
    for row in students:
        c.execute("""INSERT OR IGNORE INTO Student VALUES (?,?,?,?,?,?,?,?);""", (row[1],
                                                            hashpw(str.encode(row[8]), gensalt(4)),
                                                            row[0], row[2], row[5],
                                                            row[10], row[9], row[3]))
        print("Processing")
        c.execute("""INSERT OR IGNORE INTO Zipcode VALUES (?,?,?);""", (int(row[3]), row[6], row[7]))

        c.execute("""INSERT OR IGNORE INTO Course VALUES (?,?,?);""", (row[11], row[12], row[13]))
        c.execute("""INSERT OR IGNORE INTO Course VALUES (?,?,?);""", (row[23], row[24], row[25]))
        c.execute("""INSERT OR IGNORE INTO Course VALUES (?,?,?);""", (row[35], row[36], row[37]))

        c.execute("""INSERT OR IGNORE INTO Sections VALUES (?,?,?,?,?);""", (row[11], row[15], row[14], row[16],
                                                                             course_prof_team.get(row[11])))
        c.execute("""INSERT OR IGNORE INTO Sections VALUES (?,?,?,?,?);""", (row[23], row[27], row[26], row[28],
                                                                             course_prof_team.get(row[23])))
        c.execute("""INSERT OR IGNORE INTO Sections VALUES (?,?,?,?,?);""", (row[35], row[39], row[38], row[40],
                                                                             course_prof_team.get(row[35])))

        c.execute("""INSERT OR IGNORE INTO Enrolls Values(?,?,?);""", (row[1], row[11], row[15]))
        c.execute("""INSERT OR IGNORE INTO Enrolls Values(?,?,?);""", (row[1], row[23], row[27]))
        c.execute("""INSERT OR IGNORE INTO Enrolls Values(?,?,?);""", (row[1], row[35], row[39]))
        c.execute("""INSERT OR IGNORE INTO Homework VALUES (?,?,?,?);""", (row[11], row[15], row[17], row[18]))
        c.execute("""INSERT OR IGNORE INTO Homework VALUES (?,?,?,?);""", (row[23], row[27], row[29], row[30]))
        c.execute("""INSERT OR IGNORE INTO Homework VALUES (?,?,?,?);""", (row[35], row[39], row[41], row[42]))
        c.execute("""INSERT OR IGNORE INTO Homework_grades VALUES(?,?,?,?,?);""", (row[1], row[11], row[15], row[17], row[19]))
        c.execute("""INSERT OR IGNORE INTO Homework_grades VALUES(?,?,?,?,?);""", (row[1], row[23], row[27], row[29], row[31]))
        c.execute("""INSERT OR IGNORE INTO Homework_grades VALUES(?,?,?,?,?);""", (row[1], row[35], row[39], row[41], row[43]))
        c.execute("""INSERT OR IGNORE INTO Exams VALUES(?,?,?,?);""", (row[11], row[15], row[20], row[21]))
        c.execute("""INSERT OR IGNORE INTO Exams VALUES(?,?,?,?);""", (row[23], row[27], row[32], row[33]))
        c.execute("""INSERT OR IGNORE INTO Exams VALUES(?,?,?,?);""", (row[35], row[39], row[44], row[45]))
        c.execute("""INSERT OR IGNORE INTO Exam_grades VALUES(?,?,?,?,?);""", (row[1], row[11], row[15], row[20], row[22]))
        c.execute("""INSERT OR IGNORE INTO Exam_grades VALUES(?,?,?,?,?);""", (row[1], row[23], row[27], row[32], row[34]))
        c.execute("""INSERT OR IGNORE INTO Exam_grades VALUES(?,?,?,?,?);""", (row[1], row[35], row[39], row[44], row[46]))
        c.execute("""INSERT OR IGNORE INTO Capstone_section VALUES(?,?,?,?);""", (row[11], row[15], None,
                                                                        capstone_sponsor_dict.get(row[11])))
        c.execute("""INSERT OR IGNORE INTO Capstone_section VALUES(?,?,?,?);""", (row[23], row[27], None,
                                                                        capstone_sponsor_dict.get(row[23])))
        c.execute("""INSERT OR IGNORE INTO Capstone_section VALUES(?,?,?,?);""", (row[35], row[39], None,
                                                                        capstone_sponsor_dict.get(row[35])))
        c.execute("""INSERT OR IGNORE INTO Capstone_Team VALUES(?,?,?,?,?);""", (row[11], row[15], course_prof_team.get(row[11]),
                                                                                 None, None))
        c.execute("""INSERT OR IGNORE INTO Capstone_Team VALUES(?,?,?,?,?);""", (row[23], row[27], course_prof_team.get(row[23]),
                                                                                 None, None))
        c.execute("""INSERT OR IGNORE INTO Capstone_Team VALUES(?,?,?,?,?);""", (row[35], row[39], course_prof_team.get(row[35]),
                                                                                 None, None))
        c.execute("""INSERT OR IGNORE INTO Capstone_Team_Members VALUES(?,?,?,?,?);""", (row[1], course_prof_team.get(row[11]),
                                                                                         row[11], row[15], None))
        c.execute("""INSERT OR IGNORE INTO Capstone_Team_Members VALUES(?,?,?,?,?);""", (row[1], course_prof_team.get(row[23]),
                                                                                        row[23], row[27], None))
        c.execute("""INSERT OR IGNORE INTO Capstone_Team_Members VALUES(?,?,?,?,?);""",(row[1], course_prof_team.get(row[35]),
                                                                                        row[35], row[39], None))
        c.execute("""INSERT OR IGNORE INTO Capstone_Grades VALUES(?,?,?,?,?,?);""", (row[11], row[15], course_prof_team.get(row[11]),
                                                                                 None, None, None))
        c.execute("""INSERT OR IGNORE INTO Capstone_Grades VALUES(?,?,?,?,?,?);""", (row[23], row[27], course_prof_team.get(row[23]),
                                                                                 None, None, None))
        c.execute("""INSERT OR IGNORE INTO Capstone_Grades VALUES(?,?,?,?,?,?);""", (row[35], row[39], course_prof_team.get(row[35]),
                                                                                 None, None, None))
c.execute("""SELECT * FROM Student Limit 3 """)
print(c.fetchall())
print()
c.execute("""SELECT * FROM Department Limit 3 """)
print(c.fetchall())
c.execute("""SELECT * FROM Professor Limit 3""")
print(c.fetchall())
print()
c.execute("""SELECT * FROM Enrolls Limit 3 """)
print(c.fetchall())
c.execute("""SELECT * FROM Homework Limit 3 """)
c.execute("""SELECT * FROM Exams Limit 3 """)
print(c.fetchall())
c.execute("""SELECT * FROM Exam_grades Limit 3 """)
print(c.fetchall())
c.execute("""SELECT * FROM Zipcode Limit 3 """)
print(c.fetchall())
c.execute("""SELECT * FROM Sections Limit 3 """)
print(c.fetchall())
#
# c.execute("""DROP TABLE IF EXISTS Student""")
# c.execute("""DROP TABLE IF EXISTS Zipcode""")
# c.execute("""DROP TABLE IF EXISTS Professor""")
# c.execute("""DROP TABLE IF EXISTS Department""")
# c.execute("""DROP TABLE IF EXISTS Course""")
# c.execute("""DROP TABLE IF EXISTS Sections""")
# c.execute("""DROP TABLE IF EXISTS Enrolls""")
# c.execute("""DROP TABLE IF EXISTS Prof_teams""")
# c.execute("""DROP TABLE IF EXISTS Prof_team_members""")
# c.execute("""DROP TABLE IF EXISTS Homework""")
# c.execute("""DROP TABLE IF EXISTS Exams""")
# c.execute("""DROP TABLE IF EXISTS Exam_grades""")
# c.execute("""DROP TABLE IF EXISTS Homework_grades""")
# c.execute("""DROP TABLE IF EXISTS Capstone_section""")
# c.execute("""DROP TABLE IF EXISTS Capstone_Team""")
# c.execute("""DROP TABLE IF EXISTS Capstone_Team_Members""")
# c.execute("""DROP TABLE IF EXISTS Capstone_grades""")


conn.commit()
conn.close()



















# @app.route('/', methods=['POST', 'GET'])
# @app.route('/home')
# def name():
#     error = None
#     if request.method == 'POST':
#         result = valid_name(request.form['FirstName'], request.form['LastName'])
#         if result:
#             return render_template('input.html', error=error, url=host, result=result)
#         else:
#             error = 'invalid input name'
#     return render_template('input.html', error=error, url=host)
# @app.route('/about')
# def about():
#     return render_template('about.html')
#
# def valid_name(first_name, last_name):
#     connection = sql.connect(':memory:')
#     connection.execute('CREATE TABLE IF NOT EXISTS users(firstname TEXT, lastname TEXT);')
#     connection.execute('INSERT INTO users (firstname, lastname) VALUES (?,?);', (first_name, last_name))
#     connection.commit()
#     cursor = connection.execute('SELECT * FROM users;')
#     return cursor.fetchall()
# app.run(debug=True, port=5001)
