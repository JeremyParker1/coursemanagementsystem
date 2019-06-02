from flask import Flask, render_template, request, flash, redirect, url_for, session
import sqlite3 as sql
from forms import LoginForm, AssignmentForm, PasswordForm, GradeForm, ChangeProfForm, SectionChangeForm,\
    DropForm, EnrollmentForm, DeleteForm, CapstoneGradeForm
from flask_bcrypt import Bcrypt
from bcrypt import checkpw, hashpw, gensalt
app = Flask(__name__)
app.config['SECRET_KEY'] = '9a3235282ad5f3873064cb6d560c97ee'
host = 'http://127.0.0.1:5001/'
bcrypt = Bcrypt(app)
@app.route('/', methods=['POST', 'GET'])
def home():
    if 'user' in session:
        session.clear()
    return render_template('home.html')

@app.route('/userhome')
def userhome():
    error = None
    if 'user' in session:
        flash(f"Welcome", 'success')
        return render_template('dashboard.html', error=error, url=host, name=session['name'])
    elif session['type'] == 'Admin':
        return render_template('dashboard.html', error=error, url=host)
    return render_template('home.html', error=error, url=host)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        redirect(url_for('userhome'))
    form = LoginForm()
    if form.validate_on_submit():
        with sql.connect('courseSystem.db') as db:
            c = db.cursor()
        find_users = """SELECT * FROM Student WHERE email = ? OR password = ?"""
        c.execute(find_users, (form.email.data, form.password.data))
        results = c.fetchall()
        if results and checkpw(str.encode(form.password.data), results[0][1]):
            flash('Login Successful', 'success')
            session['user'] = results[0][0]
            session['name'] = results[0][2]
            session['type'] = 'Student'
            return redirect(url_for('userhome'))
        else:
            flash('Login Unsuccessful', 'danger')
        c.close()
    return render_template('login.html', title='Login', form=form)

@app.route('/facultyLogin', methods=['GET', 'POST'])
def facultyLogin():
    if 'user' in session:
        redirect(url_for('userhome'))
    form = LoginForm()
    if form.validate_on_submit():
        with sql.connect('courseSystem.db') as db:
            c = db.cursor()
        find_users = """SELECT * FROM Professor WHERE email = ? OR password = ?"""
        c.execute(find_users, (form.email.data, form.password.data))
        results = c.fetchall()
        print(results)
        if results and checkpw(str.encode(form.password.data), results[0][1]):
            flash('Login Successful', 'success')
            session['user'] = results[0][0]
            session['name'] = results[0][2]
            session['type'] = 'Faculty'
            return redirect(url_for('userhome'))
        else:
            flash('Login Unsuccessful', 'danger')
        c.close()
    return render_template('facultyLogin.html', title='Faculty Login', form=form)


@app.route('/adminLogin', methods=['GET', 'POST'])
def adminLogin():
    if 'user' in session:
        redirect(url_for('userhome'))
    form = LoginForm()
    if form.validate_on_submit():
            if form.email.data == 'admin@lionstate.edu' and form.password.data == 'admin':
                session['type'] = 'Admin'
                return redirect(url_for('userhome'))
            else:
                flash('Login Unsuccessful', 'danger')
    return render_template('facultyLogin.html', title='Faculty Login', form=form)


@app.route('/courses', methods=['GET','POST'])
def courses(): # TODO: THIS IS A LOT OF STUFF FOR THE ROUTES PAGE.
                # I KNOW THAT I SHOULD GET AROUND TO ORGANIZING IT BETTER
    with sql.connect('courseSystem.db') as db:
                    c = db.cursor()
    if ('user' in session) and (session['type'] =='Student'):
        find_course_info = """SELECT E.course_id, E.section_no, C.course_name
                              FROM Student S, Enrolls E, Course C, Sections S2
                              WHERE S.email = ? AND S.email = E.student_email AND E.course_id = C.course_id
                              AND S2.sec_no = E.section_no AND E.course_id = S2.course_id"""
        c.execute(find_course_info, (session['user'],))
        studentCourseInfo = c.fetchall()
        c.close()
        return render_template('courses.html', title='Courses', usertype=session['type'], courseinfo=studentCourseInfo)
    elif('user' in session) and (session['type'] == 'Faculty'):
        #TODO: insert faculty info here
        courses_taught = """SELECT S.course_id, S.sec_no
                            FROM Sections S, Prof_team_members PTM 
                            WHERE S.prof_team_id = PTM.team_id AND PTM.prof_email = ?"""
        c.execute(courses_taught, (session['user'],))
        prof_courses = c.fetchall()
        return render_template('courses.html', title='Courses', usertype=session['type'], prof_courses=prof_courses)
    elif(session['type'] == 'Admin'):
        assigned_courses = """SELECT S.course_id, S.sec_no, S.limits, P.name
                         FROM Sections S, Prof_team_members PTM, Professor P
                         WHERE PTM.team_id = S.prof_team_id AND P.email = PTM.prof_email 
                         """
        c.execute(assigned_courses)
        courses = sorted(c.fetchall())
        print(courses)
        enrolled_students = """SELECT E.course_id, E.section_no, count(*)
                               FROM Enrolls E 
                               GROUP BY E.course_id, E.section_no"""
        c.execute(enrolled_students)
        enrollmentNum = sorted(c.fetchall())
        course_infoSub = []
        course_info = []
        form = ChangeProfForm()
        noTeachers = """SELECT DISTINCT S.course_id, S.sec_no
                        FROM Sections S, Prof_team_members PTM
                        WHERE S.prof_team_id NOT IN (Select team_id FROM Prof_team_members)"""
        c.execute(noTeachers)
        noInstructors = c.fetchall()
        everyCourse = """SELECT DISTINCT S.course_id, S.sec_no FROM Sections S"""
        c.execute(everyCourse)
        everyCourse = c.fetchall()
        courseTuple = list(dict.fromkeys([(course[0], course[0]) for course in everyCourse]))
        sectionTuple = list(dict.fromkeys([(course[1], course[1]) for course in everyCourse]))
        professorTuple = list(dict.fromkeys([(course[3], course[3]) for course in courses]))
        form.course.choices = courseTuple
        form.section.choices = sectionTuple
        form.professor.choices = professorTuple
        if form.validate_on_submit():
            print("worked")
            retrieveCourse = """SELECT S.prof_team_id, P.email
                                FROM Sections S, Professor P
                                WHERE S.course_id=? AND S.sec_no=? AND P.name=?"""
            c.execute(retrieveCourse, (form.course.data, form.section.data, form.professor.data))
            newCourse = c.fetchall()
            newProfessor = newCourse[0][1]
            newTeamID = newCourse[0][0]
            newTeacher = """UPDATE Prof_team_members
                            SET team_id = ?
                            WHERE prof_email = ?"""
            c.execute(newTeacher, (newTeamID, newProfessor))
            db.commit()
            c.close()
        for x in range(len(enrollmentNum)):
            for y in range(len(enrollmentNum[x])):
                course_infoSub.append(enrollmentNum[x][y])
            course_infoSub.append(courses[x][2])
            course_infoSub.append(courses[x][3])
            course_info.append(course_infoSub)
            course_infoSub = []
        print(course_info)
        c.close()
        #TODO: Give Admin Add/Remove Capabilties in regards to students and faculty to courses
        return render_template('courses.html', title='Courses', usertype=session['type'], form=form,
                               noInstructors=noInstructors, courses=course_info)
    else:
        return render_template('home.html', title='Courses')

@app.route('/courses/studentEnrollment', methods=['GET','POST'])
def studentEnrollment():
    form = EnrollmentForm()
    with sql.connect('courseSystem.db') as db:
        c = db.cursor()
    all_courses ="""SELECT DISTINCT S.course_id, S.sec_no FROM Sections S"""
    c.execute(all_courses)
    courses = c.fetchall()
    form.course.choices = list(dict.fromkeys([(course[0],course[0]) for course in courses]))
    form.section.choices = list(dict.fromkeys([(course[1],course[1]) for course in courses]))
    if form.validate_on_submit():
        print('valid')
        enroll ="""INSERT INTO Enrolls VALUES (?,?,?)"""
        c.execute(enroll, (form.email.data, form.course.data, form.section.data))
        db.commit()
        c.close()

    return render_template('studentEnrollment.html', form=form, title='Enroll a student in a class')

@app.route('/courses/studentSectionStat/<course>/<section>/<amount>/<limit>', methods=['GET','POST'])
def studentSectionStat(course, section, amount, limit):
    sectionForm = SectionChangeForm()
    dropForm = DropForm()
    with sql.connect('courseSystem.db') as db:
        c = db.cursor()
    findEnrollments = """SELECT E.student_email FROM Enrolls E WHERE E.course_id=? and E.section_no=?"""
    c.execute(findEnrollments, (course, section))
    enrollments = c.fetchall()
    all_courses = """SELECT S.course_id, S.sec_no FROM SECTIONS S"""
    c.execute(all_courses)
    courses = c.fetchall()
    #sectionForm.course.choices = list(dict.fromkeys([(course[0], course[0]) for course in courses]))
    sectionForm.section.choices = list(dict.fromkeys([(course[1], course[1]) for course in courses]))
    sectionForm.email.choices = [(student[0], student[0]) for student in enrollments]
    dropForm.email.choices = sectionForm.email.choices
    if sectionForm.validate_on_submit():
        changeClass = """UPDATE Enrolls
                         SET section_no=?
                         WHERE student_email=? AND course_id=? AND section_no=?"""
        c.execute(changeClass, (sectionForm.section.data, sectionForm.email.data, course, section))
        db.commit()
    if dropForm.validate_on_submit():
        dropClass = """DELETE FROM Enrolls
                        WHERE student_email = ? AND course_id=? AND section_no=?"""
        c.execute(dropClass, (dropForm.email.data, course, section))
        db.commit()
    return render_template('studentSectionStat.html', title='Student Enrollments for '+course+' Section: '+section,
                           enrollments=enrollments, amount=amount, limit=limit, form=sectionForm, dropForm=dropForm)


@app.route('/courseAssignments')
def courseAssignments():
    if ('user' in session) and (session['type'] =='Student'):
        return render_template('courseAssignments.html', title='Assignments')
    else:
        return render_template('home.html')

@app.route('/courseDetails/<course>/<section>')
def courseDetails(course, section):
    if ('user' in session) and (session['type'] == 'Student'):
        with sql.connect('courseSystem.db') as db:
            c = db.cursor()
        find_course_info = """SELECT DISTINCT C.course_id, C.course_description, S2.section_type
                              FROM  Course C, Sections S2
                              WHERE C.course_id = ? AND C.course_id = S2.course_id"""
        c.execute(find_course_info, (course,))
        courseInfo = c.fetchall()[0]
        find_course_faculty = """SELECT DISTINCT P.name, P.email, P.office_address, D.dept_name
                                 FROM Course C, Sections S, Professor P, Prof_team_members PT, Department D
                                 WHERE S.course_id = C.course_id AND S.prof_team_id=PT.team_id AND P.email = PT.prof_email
                                AND S.course_id = ? AND P.department = D.dept_id"""
        c.execute(find_course_faculty, (course,))
        faculty_course_info = c.fetchall()[0]
        #TODO: implement capstone team details
        findMembers = """SELECT S.name, S.email FROM Student S Where S.email IN
                        (SELECT CTM.student_email
                         FROM Capstone_Team_Members CTM
                         WHERE CTM.team_number = 
                         (SELECT CTM.team_number FROM 
                         Capstone_Team_Members CTM
                         WHERE CTM.student_email=? AND CTM.course_id=? AND CTM.sec_no=?))
                         """
        c.execute(findMembers,(session['user'], course, section))
        findTeam = c.fetchall()
        teamNumber = """SELECT CTM.team_number FROM Capstone_Team_Members CTM WHERE CTM.student_email=?"""
        c.execute(teamNumber, (session['user'],))
        teamNumber = c.fetchall()[0][0]
        print(teamNumber)
        hw = """SELECT DISTINCT H.hw_no
                      FROM Homework H, Sections S
                      WHERE S.course_id = H.course_id AND S.course_id = ? AND S.sec_no = ?"""
        c.execute(hw, (course, section))
        homework = c.fetchall()
        ex = """SELECT DISTINCT E.exam_no
                FROM Exams E, Sections S
                WHERE S.course_id = E.course_id AND S.course_id = ? AND S.sec_no = ?"""
        c.execute(ex, (course, section))
        exams = c.fetchall()
        projects = """SELECT C.project_no, C.grade FROM Capstone_grades C WHERE C.team_number=? AND C.course_id=? AND C.sec_no=?"""
        c.execute(projects, (teamNumber, course, section))
        projects = c.fetchall()
        projectGrades = []
        for project in projects:
            if project[0]:
                projectGrades.append(tuple([project[1]]))
        print(projectGrades)
        sectionType = """SELECT S.section_type From Sections S WHERE S.course_id=? AND S.sec_no=?"""
        examGrades = """SELECT E.grades from Exam_grades E WHERE E.course_id=? AND E.sec_no=? and E.student_email=?"""
        homeworkGrades = """SELECT H.grade from Homework_grades H WHERE H.course_id=? AND H.sec_no=? and H.student_email=?"""
        c.execute(sectionType, (course,section))
        sectionType = c.fetchall()[0][0]
        print(sectionType)
        c.execute(examGrades, (course,section,session['user']))
        examGrades = c.fetchall()
        c.execute(homeworkGrades, (course,section,session['user']))
        homeworkGrades = c.fetchall()
        if sectionType == 'Reg':
            overallGrades = examGrades+homeworkGrades
        else:
            overallGrades = projectGrades+homeworkGrades
        print(overallGrades)
        sumGrades = 0
        for grade in overallGrades:
             sumGrades += grade[0]

        averageGrade = round(sumGrades/(len(overallGrades)), 2)
        if averageGrade > 90:
            letterGrade = 'A'
        elif averageGrade > 85 and averageGrade < 90:
            letterGrade = 'B+'
        elif averageGrade > 80 and averageGrade < 85:
            letterGrade = 'B'
        elif averageGrade > 75 and averageGrade < 80:
            letterGrade = 'C+'
        elif averageGrade > 70 and averageGrade < 75:
            letterGrade = 'C'
        else:
            letterGrade = 'F'
        c.close()
        return render_template('courseDetails.html', title=(course+" Section: "+section), courseInfo=courseInfo,
                                  courseProf=faculty_course_info, homework=homework, projects=projects,
                                course=course, section=section, exams=exams, members=findTeam, teamNumber=teamNumber,
                               averageGrade=averageGrade, letterGrade=letterGrade)
    else:
        return render_template('home.html')


@app.route('/courseDetails/<course>/<section>/team<teamNumber>/project<project>')
def projectDetails(course, section, teamNumber, project):
    if ('user' in session) and (session['type'] =='Student'):
        projects = project[1]
        with sql.connect('courseSystem.db') as db:
            c = db.cursor()
        projDesc = """SELECT C.project_desc FROM Capstone_Team C WHERE C.course_id=? AND C.sec_no=? AND C.project_no=?"""
        c.execute(projDesc, (course,section, projects))
        projDesc = c.fetchall()[0]
        projGrade = """SELECT C.grade FROM Capstone_grades C WHERE C.course_id=? AND C.sec_no=? and C.team_number=? AND C.project_no=?"""
        c.execute(projGrade, (course, section, teamNumber, projects))
        projGrade = c.fetchall()[0]
        print(projDesc)
        c.close()
        return render_template('projectDetails.html', title=("Project: "+project[1]), projDesc=projDesc, projGrade=projGrade)
    else:
        return render_template('home.html')

@app.route('/courseDetails/<course>/<section>/homework<homework>')
def homeworkDetails(course, section, homework):
    if ('user' in session) and (session['type'] == 'Student'):
        with sql.connect('courseSystem.db') as db:
            c = db.cursor()
        homeworkDetails = """SELECT DISTINCT H.hw_no, H.hw_details
                FROM Homework H, Course C, Sections S
                WHERE H.hw_no = ? AND C.course_id = ? AND S.sec_no = ?"""
        c.execute(homeworkDetails, (homework, course, section))
        hwDetails = c.fetchall()[0]
        homeworkGrade = """SELECT HG.grade
                     FROM Homework_grades HG 
                     WHERE HG.student_email = ? AND HG.hw_no = ? AND HG.course_id = ? AND HG.sec_no = ?"""
        c.execute(homeworkGrade, (session['user'], homework, course, section))
        hwGrade = c.fetchall()[0][0]
        averagehiLo = """SELECT min(HG.grade), round(avg(HG.grade),2), max(HG.grade)
                     FROM Homework_grades HG
                     WHERE HG.hw_no=? AND HG.course_id=? AND HG.sec_no=?"""
        c.execute(averagehiLo, (homework, course, section))
        hwStats = c.fetchall()[0]
        c.close()
        return render_template('homeworkDetails.html', title=("Homework: " + homework), hwDetails=hwDetails,
                               hwGrade=hwGrade, hwStats=hwStats)
    else:
        return render_template('home.html')


@app.route('/courseDetails/<course>/<section>/exam<exam>')
def examDetails(course, section, exam):
    with sql.connect('courseSystem.db') as db:
        c = db.cursor()
    examDetails = """SELECT DISTINCT E.exam_no, E.exam_details
                     FROM Exams E, Course C, Sections S
                     WHERE E.exam_no = ? AND C.course_id = ? AND S.sec_no = ?"""
    c.execute(examDetails, (exam, course, section))
    exDetails = c.fetchall()[0]
    examGrade = """SELECT EG.grades
                 FROM Exam_grades EG 
                 WHERE EG.student_email = ? AND EG.exam_no = ? AND EG.course_id = ? AND EG.sec_no = ?"""
    c.execute(examGrade, (session['user'], exam, course, section))
    exGrade = c.fetchall()[0][0]
    averagehiLo = """SELECT min(EG.grades), round(avg(EG.grades),2), max(EG.grades)
                 FROM main.Exam_grades EG
                 WHERE EG.exam_no=? AND EG.course_id=? AND EG.sec_no=?"""
    c.execute(averagehiLo, (exam, course, section))
    examStats = c.fetchall()[0]
    print(examStats)
    print(exDetails)
    print(exGrade)
    c.close()
    return render_template('examDetails.html', title=('Exam: '+exam), exDetails=exDetails,
                           exGrade=exGrade, examStats=examStats)
@app.route('/profile')
def profile():
    if session['type'] == 'Student':
        with sql.connect('courseSystem.db') as db:
            c = db.cursor()
        info = """SELECT * FROM Student S WHERE S.email = ?"""
        c.execute(info, (session['user'],))
        studentInfo = c.fetchall()[0]
        home = """SELECT * FROM Zipcode Z WHERE Z.zipcode = ?"""
        c.execute(home, (studentInfo[7],))
        homeAddress = c.fetchall()[0]
        c.close()
        return render_template('profile.html', title=studentInfo[2]+"'s Profile", usertype=session['type'], studentInfo=studentInfo,
                               homeAddress=homeAddress)
    elif session['type'] == 'Faculty':
        with sql.connect('courseSystem.db') as db:
            c = db.cursor()
        info = """SELECT * FROM Professor P WHERE P.email = ?"""
        c.execute(info, (session['user'],))
        profInfo = c.fetchall()[0]
        c.close()
        return render_template('profile.html', title=profInfo[2]+"'s Profile", usertype=session['type'], profInfo=profInfo)
    else:
        return render_template('profile.html', title='Profile')


@app.route('/changePassword', methods=['GET','POST'])
def changePassword():
    form = PasswordForm()
    if session['type'] == 'Student' or session['type'] == 'Faculty':
        if form.validate_on_submit():
            with sql.connect('courseSystem.db') as db:
                c = db.cursor()
            if session['type'] == 'Student':
                find_users = """SELECT * FROM Student S WHERE S.email = ?"""
            else:
                find_users = """SELECT * FROM Professor P WHERE P.email = ?"""
            c.execute(find_users, (session['user'],))
            results = c.fetchall()
            if results and checkpw(str.encode(form.password.data), results[0][1]) and\
                    (form.newPassword.data == form.confirm.data):
                if session['type'] == 'Student':
                    changePassword = """UPDATE Student
                                        SET password=?
                                        WHERE email=?"""
                else:
                    changePassword ="""UPDATE Professor
                                       SET password=?
                                       WHERE email=?"""
                print(form.newPassword.data)
                c.execute(changePassword, (hashpw(str.encode(form.newPassword.data), gensalt(4)), session['user']))
                db.commit()
                c.close()
            return redirect(url_for('userhome'))
        return render_template('changePassword.html', form=form)
    elif session['type'] == 'Admin':
        return render_template('changePassword.html')
    else:
        return render_template('home.html')

@app.route('/<course>/<section>/createAssignment', methods=['GET','POST'])
def createAssignment(course, section):
    form = AssignmentForm()
    form.type.choices = [('homework', 'homework'),('exam', 'exam'), ('project','project')]
    with sql.connect('courseSystem.db') as db:
        c = db.cursor()
    findEnrolled = """SELECT E.student_email FROM Enrolls E WHERE E.course_id=? AND E.section_no=?"""
    c.execute(findEnrolled, (course, section))
    students = c.fetchall()
    for email in students:
        print(email[0])
    findTeamID = """SELECT S.prof_team_id From Sections S WHERE S.course_id=? AND S.sec_no=?"""
    c.execute(findTeamID, (course, section))
    teamID = c.fetchall()[0][0]
    print(teamID)
    findTeamNums = """SELECT DISTINCT CTM.team_number from Capstone_Team_Members CTM"""
    c.execute(findTeamNums)
    findTeamNums = c.fetchall()
    findTeamNums = [team[0] for team in findTeamNums if team[0] != 'None' and team[0] != None]
    if form.validate_on_submit():
        if form.type.data =='homework':
            newAssignment = """INSERT INTO Homework VALUES (?,?,?,?)"""
            c.execute(newAssignment, (course, section, form.number.data, form.content.data))
            newAssignment = """INSERT INTO Homework_grades VALUES (?,?,?,?,?)"""
            for email in students:
                c.execute(newAssignment, (email[0], course, section, form.number.data, None))
        elif form.type.data =='exam':
            newAssignment = """INSERT INTO Exams VALUES (?,?,?,?)"""
            c.execute(newAssignment, (course, section, form.number.data, form.content.data))
            newAssignment = """INSERT INTO Exam_grades VALUES (?,?,?,?,?)"""
            for email in students:
                c.execute(newAssignment, (email[0], course, section, form.number.data, None))
        elif form.type.data =='project':
            newAssignment = """INSERT INTO Capstone_Team VALUES (?,?,?,?,?)"""
            c.execute(newAssignment, (course, section, teamID, form.number.data, form.content.data))
            for team in findTeamNums:
                newAssignment = """INSERT OR IGNORE INTO Capstone_grades VALUES(?,?,?,?,?,?)"""
                c.execute(newAssignment, (course, section, teamID, team, None, form.number.data))
                print(form.number.data,"???")
        db.commit()
        c.close()
        return redirect(url_for('classSectionDetails', course=course, section=section))
    return render_template('createAssignment.html', title='Create Assignment', usertype=session['type'], form=form)


@app.route('/classSectionDetails/<course>/<section>', methods=['GET','POST'])
def classSectionDetails(course, section):
    with sql.connect('courseSystem.db') as db:
        c = db.cursor()
    findHomeworks = """SELECT DISTINCT H.hw_no FROM Homework H WHERE H.course_id = ? AND H.sec_no = ?"""
    c.execute(findHomeworks, (course, section))
    homeworks = c.fetchall()
    findExams = """SELECT DISTINCT E.exam_no FROM Exams E WHERE E.course_id = ? AND E.sec_no = ?"""
    c.execute(findExams, (course, section))
    exams = c.fetchall()
    findProjects = """SELECT DISTINCT C.project_no FROM Capstone_Team C WHERE C.course_id=? AND C.sec_no=?"""
    c.execute(findProjects,(course, section))
    projects = c.fetchall()
    findType = """SELECT S.section_type From Sections S WHERE S.course_id = ? AND S.sec_no = ?"""
    c.execute(findType, (course, section))
    sectionType = c.fetchall()
    if sectionType[0][0] == 'Cap':
        capStudents = """SELECT DISTINCT CTM.student_email, CTM.team_id, CTM.sec_no, CTM.Team_Number
                       FROM Prof_team_members PTM, Capstone_Team_Members CTM, Sections S
                       WHERE PTM.prof_email=? AND PTM.team_id=CTM.team_id AND CTM.course_id=? and CTM.sec_no=?"""
        c.execute(capStudents, (session['user'], course, section))
        capStudents = sorted(c.fetchall())
        print(capStudents)
        findTeams = """SELECT CTM.student_email
                       FROM Capstone_Team_Members CTM, Prof_team_members PTM
                       WHERE PTM.prof_email=? AND PTM.team_id=CTM.team_id AND CTM.course_id=? AND CTM.sec_no=?"""
        c.execute(findTeams, (session['user'], course, section))
        if request.method == 'POST':
            student = request.form['student'].split(',')
            addTeam = """UPDATE Capstone_Team_Members
                         SET team_number = ?
                         WHERE student_email=? AND course_id=? AND sec_no=? """
            c.execute(addTeam, (student[1], student[0], course, section))
            db.commit()
            addCapstone = """INSERT OR IGNORE INTO Capstone_grades VALUES (?,?,?,?,?,?)"""
            c.execute(addCapstone, (course, section, capStudents[0][1], student[1], None, None))
            db.commit()

            c.close()
            print(student)
            redirect(url_for('classSectionDetails', course=course,section=section))
        return render_template('classSectionDetails.html', title=course + ' Section: ' + section,
                               usertype=session['type'],
                               homeworks=homeworks, exams=exams, projects = projects,
                               sectionType=sectionType, course=course, section=section,
                               capStudents=capStudents)
        #TODO Fix refresh issue, give faculty capabiltiy to give scores to individuals and teams
        #ev4n7hoh
    c.close()

    return render_template('classSectionDetails.html', title=course+' Section: '+section, usertype=session['type'],
                           homeworks=homeworks, exams=exams, sectionType=sectionType, course=course, section=section)


@app.route('/classSectionDetails/<course>/<section>/<type>/<assignment><number>', methods=['GET','POST'])
def assignmentGrades(course, section, type, assignment, number):
    with sql.connect('courseSystem.db') as db:
        c = db.cursor()
    if assignment == 'homework':
        findStudents = """SELECT HG.student_email, HG.grade 
                        FROM Homework_grades HG
                        WHERE HG.course_id=? AND HG.sec_no=? AND HG.hw_no=?"""
        c.execute(findStudents, (course, section, number))

    elif assignment == 'exam':
        findStudents = """SELECT EG.student_email, EG.grades
                          FROM Exam_grades EG 
                          WHERE EG.course_id=? AND EG.sec_no=? AND EG.exam_no=?"""
        c.execute(findStudents, (course, section, number))
    elif assignment == 'project':
        findStudents = """SELECT DISTINCT CG.team_number, CG.grade
                          FROM Capstone_grades CG 
                          WHERE CG.course_id=? AND CG.sec_no=? AND CG.project_no=?"""
        c.execute(findStudents, (course, section, number))
    grades = c.fetchall()
    findEnrolled = """SELECT E.student_email FROM Enrolls E WHERE E.course_id=? AND E.section_no=?"""
    c.execute(findEnrolled, (course, section))
    emails = c.fetchall()
    form = GradeForm()
    delForm = DeleteForm()
    print(grades)
    capForm = CapstoneGradeForm()
    emails = [(grade[0], grade[0]) for grade in emails]
    teamNum = list(dict.fromkeys([(grade[0], grade[0]) for grade in grades if grade[0]]))
    form.email.choices = emails
    print(teamNum)
    if assignment =='project':
         capForm.teamNum.choices = teamNum
         if capForm.validate_on_submit() and assignment == 'project':
             newGrade = """UPDATE Capstone_grades
                           SET grade=?
                           WHERE team_number=? AND course_id=? AND sec_no=? AND project_no=?"""
             c.execute(newGrade, (capForm.newGrade.data, capForm.teamNum.data, course, section, number))
             db.commit()
             c.close()
         elif delForm.validate_on_submit():
             delete = """DELETE FROM Capstone_Team WHERE course_id=? AND sec_no=? AND project_no=?"""
             c.execute(delete, (course, section, number))
             db.commit()
             # delete = """DELETE FROM Capstone_grades WHERE course_id=? AND sec_no=? AND project_no=?"""
             # c.execute(delete, (course, section, number))
             # db.commit()
             c.close()
             return redirect(url_for('classSectionDetails', course=course, section=section))
    if form.validate_on_submit() and assignment == 'homework':
        newGrade = """UPDATE Homework_grades
                      SET grade = ?
                      WHERE Homework_grades.student_email = ? AND course_id=? AND sec_no=? AND hw_no=?"""
        c.execute(newGrade, (form.newGrade.data, form.email.data, course, section, number))
        db.commit()
        c.close()
    elif form.validate_on_submit() and assignment =='exam':
        newGrade = """UPDATE Exam_grades
                      SET grades = ?
                      WHERE Exam_grades.student_email = ? AND course_id=? AND sec_no=? AND exam_no=?"""
        c.execute(newGrade, (form.newGrade.data, form.email.data, course, section, number))
        db.commit()
        c.close()
    elif delForm.validate_on_submit() and assignment =='homework':
        delete = """DELETE FROM Homework WHERE course_id=? AND sec_no=? AND hw_no=?"""
        c.execute(delete, (course, section, number))
        db.commit()
        delete = """DELETE FROM Homework_grades WHERE course_id=? AND sec_no=? AND hw_no=?"""
        c.execute(delete, (course, section, number))
        db.commit()
        c.close()
        return redirect(url_for('classSectionDetails', course=course, section=section))
    elif delForm.validate_on_submit() and assignment == 'exam':
        delete = """DELETE FROM Exams WHERE course_id=? AND sec_no=? AND exam_no=?"""
        c.execute(delete, (course, section, number))
        db.commit()
        delete = """DELETE FROM Exam_grades WHERE course_id=? AND sec_no=? AND exam_no=?"""
        c.execute(delete, (course, section, number))
        db.commit()
        c.close()
        return redirect(url_for('classSectionDetails', course=course, section=section))

    return render_template('assignmentGrades.html', title=assignment.capitalize()+": "+number+' Student Scores',
                           grades=grades, assignment=assignment, form=form, delForm=delForm, capForm=capForm,
                           sectionType=type)

# def valid_name(first_name, last_name):
#     connection = sql.connect(':memory:')
#     connection.execute('CREATE TABLE IF NOT EXISTS users(firstname TEXT, lastname TEXT);')
#     connection.execute('INSERT INTO users (firstname, lastname) VALUES (?,?);', (first_name, last_name))
#     connection.commit()
#     cursor = connection.execute('SELECT * FROM users;')
#     connection.close()
#     return cursor.fetchall()

app.run(debug=True, port=5001)
#TODO: Assign capstone team grades
#TODO: make faculty assignments, exams, projects

