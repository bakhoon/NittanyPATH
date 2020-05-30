from flask import Flask, render_template, request, redirect
import sqlite3 as sql
import forCsvtoSQLite
from datetime import datetime
import hashlib


app = Flask(__name__)
# app.static_folder = 'static'

myid = None
mypw = None
temppostnum = None
temptitle = None
tempemail = None
tempdate = None
temptime = None
tempflname = None
tempsection = None
tempcourse = None
temphomework = None
temphwdesc = None
tempexam = None
tempexamdesc = None
enrollnotice = ' '
takingnotice = ' '
latedropnotice = ' '


# csvfile.get_data()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        global myid
        myid = request.form['iemail']
        global mypw
        original = request.form['ipassword']

        mypwhashed = hashlib.md5()
        mypwhashed.update(original.encode('utf8'))
        mypw = mypwhashed.hexdigest()
        print(mypw)

        connection = sql.connect('database.db')
        cursor = connection.execute(
            'Select S.semail, S.password FROM Students S')
        getSemail = cursor.fetchall()
        cursor = connection.execute('Select TA.semail, TA.password FROM TA')
        getTAemail = cursor.fetchall()
        cursor = connection.execute(
            'Select P.pemail, P.password FROM Professors P')
        getPemail = cursor.fetchall()
        setStudent = []
        for set in getSemail:
            setStudent.append([set[0], set[1]])
        setTA = []
        for set in getTAemail:
            setTA.append([set[0], set[1]])
        setProfessor = []
        for set in getPemail:
            setProfessor.append([set[0], set[1]])
        if [myid, mypw] in setStudent:
            return redirect('/student')
        elif [myid, mypw] in setTA:
            return redirect('/TA')
        elif [myid, mypw] in setProfessor:
            return redirect('/professor')
        else:
            notice = "ID is invalid, or Password is wrong. Please try again."
            return render_template('login.html', error=error, notice=notice)
    return render_template('login.html', error=error)


@app.route('/student', methods=['POST', 'GET'])
def student():
    error = None
    connection = sql.connect('database.db')
    # my info
    cursor = connection.execute(
        'SELECT S.firstname, S.lastname, S.semail, S.age, S.gender, S.major FROM Students S WHERE ? = S.semail AND ? = S.password;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    mygender = None
    if myinfo[0][4] == 'F':
        mygender = 'Female'
    elif myinfo[0][4] == 'M':
        mygender = 'Male'
    changemyinfo = [myinfo[0][0] + ' ' + myinfo[0][1],
                    myinfo[0][2], myinfo[0][3], mygender, myinfo[0][5]]
    setinfo = [(None, None, None, None, None)]
    setinfo[0] = changemyinfo
    # my course
    cursor1 = connection.execute('SELECT C.cid, C.cname, Sec.sec_no, P.firstname, P.lastname, P.pemail, P.office_num, P.office_building '
                                 'FROM Students S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
                                 'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
                                 'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
                                 (myid, mypw))

    myschedule = cursor1.fetchall()
    setschedule = []  # append
    for set in myschedule:
        profname = 'Professor ' + set[3] + ' ' + set[4]
        profemail = set[5] + '@Nittanystate.edu'
        setschedule.append([set[0], set[1], set[2], profname,
                            profemail, set[6] + ' ' + set[7]])
    # my coming up
    cursor = connection.execute('SELECT E.cid, H.hw_no, H.hwdesc, HG.grade '
                                'FROM Students S, Enrolls E, Homeworks H, Homeworks_grade HG '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = H.sec_no AND E.cid = H.cid '
                                'AND S.semail = HG.semail AND H.cid = HG.cid AND H.sec_no = HG.sec_no AND H.hw_no = HG.hw_no;',
                                (myid, mypw))
    myhwdue = cursor.fetchall()
    cursor = connection.execute('SELECT E.cid, Ex.exam_no, Ex.examdesc, ExG.grade '
                                'FROM Students S, Enrolls E, Exams Ex, Exams_grade ExG '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Ex.sec_no AND E.cid = Ex.cid '
                                'AND S.semail = ExG.semail AND E.cid = ExG.cid AND Ex.sec_no = ExG.sec_no AND Ex.exam_no = ExG.exam_no;',
                                (myid, mypw))
    myexam = cursor.fetchall()
    mydue = []
    for set in myhwdue:
        tempname = 'Homework ' + str(set[1])
        tempset = [set[0], tempname, set[2], set[3]]
        mydue.append(tempset)
    for set in myexam:
        tempname = 'Exam ' + str(set[1])
        tempset = [set[0], tempname, set[2], set[3]]
        mydue.append(tempset)
    if setinfo:
        return render_template('main.html', error=error, myinfo=setinfo, myschedule=setschedule, mydue=mydue)
    else:
        error = 'invalid input name'
    return render_template('main.html', error=error)


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT S.firstname, S.lastname, S.password, S.semail, S.age, S.gender, S.major, S.phone, S.street, S.zipcode, Ct.city, Ct.state FROM Students S, Zipcodes Z, Cities Ct '
        'WHERE ? = S.semail AND ? = S.password AND Z.zipcode = S.zipcode AND Z.city = Ct.city;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    tempgender = None
    getinfo = []
    for set in myinfo:
        if set[5] == 'F':
            tempgender = 'Female'
        elif set[5] == 'M':
            tempgender = 'Male'
        getinfo.append([set[0], set[1], set[2], set[3], set[4],
                        tempgender, set[6], set[7], set[8], set[9], set[10], set[11]])
    if getinfo:
        return render_template('profile.html', error=error, myinfo=getinfo)
    else:
        error = 'invalid input name'
    return render_template('profile.html', error=error)


@app.route('/changeprofile', methods=['POST', 'GET'])
def changeprofile():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT S.firstname, S.lastname, S.password, S.semail, S.age, S.gender, S.major, S.phone, S.street, S.zipcode, Ct.city, Ct.state FROM Students S, Zipcodes Z, Cities Ct '
        'WHERE ? = S.semail AND ? = S.password AND Z.zipcode = S.zipcode AND Z.city = Ct.city;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    getinfo = []
    for set in myinfo:
        if set[5] == 'F':
            tempgender = 'Female'
        elif set[5] == 'M':
            tempgender = 'Male'
        getinfo.append([set[0], set[1], set[2], set[3], set[4],
                        tempgender, set[6], set[7], set[8], set[9], set[10], set[11]])
    if request.method == 'POST':
        getfname = request.form['fname']
        getlname = request.form['lname']
        getstreet = request.form['street']
        getzipcode = int(request.form['zipcode'])
        getcity = request.form['city']
        getstate = request.form['state']
        getphone = request.form['phone']
        connection.execute(
            'UPDATE Students '
            'SET firstname = ?, lastname = ?, street = ?, zipcode = ?, phone = ? '
            'WHERE semail = ? AND password = ?;',
            (getfname, getlname, getstreet, getzipcode, getphone, myid, mypw))
        connection.commit()
        cursor = connection.execute('SELECT Z.zipcode FROM Zipcodes Z;')
        zipcodess = cursor.fetchall()
        zipcodes = []
        for set in zipcodess:
            zipcodes.append(set[0])
        cursor = connection.execute('SELECT C.city FROM Cities C;')
        citiess = cursor.fetchall()
        cities = []
        for set in citiess:
            cities.append(set[0])
        if getzipcode in zipcodes:
            connection.execute(
                'UPDATE Zipcodes '
                'SET city = ? '
                'WHERE zipcode = ?;',
                (getcity, getzipcode))
            connection.commit()
        else:
            connection.execute(
                'INSERT INTO Zipcodes (zipcode, city) VALUES (?,?)', (getzipcode, getcity))
            connection.commit()
        if getcity in cities:
            connection.execute(
                'UPDATE Cities '
                'SET state = ? '
                'WHERE city = ?;',
                (getstate, getcity))
            connection.commit()
        else:
            connection.execute(
                'INSERT INTO Cities (city, state) VALUES (?,?)', (getcity, getstate))
            connection.commit()
        return redirect('/profile')
    if getinfo:
        return render_template('changeprofile.html', error=error, myinfo=getinfo)
    else:
        error = 'invalid input name'
    return render_template('changeprofile.html', error=error)


@app.route('/changepassword', methods=['POST', 'GET'])
def changepassword():
    global mypw
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT S.password FROM Students S '
        'WHERE ? = S.semail AND ? = S.password;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    if request.method == 'POST':
        getoldpw = request.form['oldpw']
        mypwhashed = hashlib.md5()
        mypwhashed.update(getoldpw.encode('utf8'))
        myoldpw = mypwhashed.hexdigest()
        getnewpw = request.form['newpw']
        mynewpwhashed = hashlib.md5()
        mynewpwhashed.update(getnewpw.encode('utf8'))
        mynewpw = mynewpwhashed.hexdigest()
        if myoldpw == mypw:
            mypw = mynewpw
            connection.execute(
                'UPDATE Students '
                'SET password = ?'
                'WHERE semail = ?;',
                (mypw, myid))
            connection.commit()
        else:
            pass
        return redirect('/profile')
    if myinfo:
        return render_template('changepassword.html', error=error, myinfo=myinfo)
    else:
        error = 'invalid input name'
    return render_template('changepassword.html', error=error)


@app.route('/classmates', methods=['POST', 'GET'])
def classmates():
    error = None
    connection = sql.connect('database.db')
    getclassmates = []
    cursor = connection.execute(
        'SELECT E2.cid, S2.semail, S2.firstname, S2.lastname, E2.sec_no, S2.age, S2.gender, S2.major '
        'FROM Students S, Enrolls E, Sections Sec, Students S2, Enrolls E2 '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = Sec.cid AND E.sec_no = Sec.sec_no AND E2.cid = Sec.cid AND E2.sec_no = Sec.sec_no AND E2.semail = S2.semail;',
        (myid, mypw))
    myclassmates = cursor.fetchall()
    cursor = connection.execute(
        'SELECT E2.cid, TA.semail, TA.firstname, TA.lastname, E2.sec_no, TA.age, TA.gender, TA.major '
        'FROM Students S, Enrolls E, Sections Sec, TA, Enrolls E2 '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = Sec.cid AND E.sec_no = Sec.sec_no AND E2.cid = Sec.cid AND E2.sec_no = Sec.sec_no AND E2.semail = TA.semail;',
        (myid, mypw))
    myclassmatet = cursor.fetchall()
    for set in myclassmates:
        getclassmates.append(set)
    for set in myclassmatet:
        getclassmates.append(set)
    if myclassmates:
        return render_template('classmates.html', error=error, myclassmates=getclassmates)
    else:
        error = 'invalid input name'
    return render_template('classmates.html', error=error)


@app.route('/course', methods=['POST', 'GET'])
def course():
    global enrollnotice
    enrollnotice = ' '
    global takingnotice
    takingnotice = ' '
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT C.cid, C.cname, Sec.sec_no, P.firstname, P.lastname, P.pemail, P.office_num, P.office_building, C.cdesc '
        'FROM Students S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
        'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
        (myid, mypw))
    myschedule = cursor1.fetchall()
    setschedule = []  # append
    for set in myschedule:
        profname = 'Professor ' + set[3] + ' ' + set[4]
        profemail = set[5] + '@Nittanystate.edu'
        cursor1 = connection.execute('SELECT Hg.grade '
                                     'FROM Students S, Enrolls E, Homeworks H, Homeworks_grade Hg '
                                     'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                     'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no '
                                     'AND Hg.cid = ? AND S.semail = Hg.semail;',
                                     (myid, mypw, set[0]))
        myhwgrade = cursor1.fetchall()
        hwgrade = []
        for set2 in myhwgrade:
            hwgrade.append(set2[0])
        cursor = connection.execute('SELECT Hg.grade '
                                    'FROM Students S, Enrolls E, Exams H, Exams_grade Hg '
                                    'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                    'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no '
                                    'AND Hg.cid = ? AND S.semail = Hg.semail;',
                                    (myid, mypw, set[0]))
        myexamgrade = cursor.fetchall()
        examgrade = []
        for set2 in myexamgrade:
            examgrade.append(set2[0])
        print('hw')
        print(hwgrade)
        print('exam')
        print(examgrade)
        tempnum = 1
        if len(examgrade) == 0 and len(hwgrade) == 0:
            setschedule.append([set[0], set[1], set[2], profname,
                                profemail, set[6] + ' ' + set[7], set[8], ' '])
        elif len(examgrade) == 0:
            finalgrade = (sum(hwgrade) / len(hwgrade))
            final2deci = "{:.2f}".format(finalgrade)
            setschedule.append([set[0], set[1], set[2], profname,
                                profemail, set[6] + ' ' + set[7], set[8], final2deci])
        elif len(hwgrade) == 0:
            finalgrade = (sum(examgrade) / len(examgrade))
            final2deci = "{:.2f}".format(finalgrade)
            setschedule.append([set[0], set[1], set[2], profname,
                                profemail, set[6] + ' ' + set[7], set[8], final2deci])
        else:
            if ' ' in examgrade or ' ' in hwgrade:
                setschedule.append(
                    [set[0], set[1], set[2], profname, profemail, set[6] + ' ' + set[7], set[8], ' '])
            else:
                finalgrade = (sum(examgrade) / len(examgrade)) * \
                    0.7 + (sum(hwgrade) / len(hwgrade)) * 0.3
                final2deci = "{:.2f}".format(finalgrade)
                setschedule.append([set[0], set[1], set[2], profname,
                                    profemail, set[6] + ' ' + set[7], set[8], final2deci])
    if setschedule:
        return render_template('course.html', error=error, myschedule=setschedule)
    else:
        error = 'invalid input name'
    return render_template('course.html', error=error)


@app.route('/homework', methods=['POST', 'GET'])
def homework():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT E.cid, H.hw_no, H.hwdesc, HG.grade '
                                'FROM Students S, Enrolls E, Homeworks H, Homeworks_grade HG '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = H.sec_no AND E.cid = H.cid '
                                'AND S.semail = HG.semail AND H.cid = HG.cid AND H.sec_no = HG.sec_no AND H.hw_no = HG.hw_no;',
                                (myid, mypw))
    hwgraded = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT E.cid, H.hw_no, H.hwdesc '
                                'FROM Students S, Enrolls E, Homeworks H '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = H.sec_no AND E.cid = H.cid;',
                                (myid, mypw))
    hwnotgraded = cursor.fetchall()
    sethw = []
    sethw2 = []
    totalhw = []
    temphw = []
    for set in hwgraded:
        sethw.append([set[0], set[1], set[2], set[3]])
    for set in hwgraded:
        temphw.append([set[0], set[1], set[2]])
    for set in hwnotgraded:
        sethw2.append([set[0], set[1], set[2], int(-1)])
    for set in sethw2:
        for setgraded in sethw:
            if [setgraded[0], setgraded[1], setgraded[2]] == [set[0], set[1], set[2]]:
                if setgraded[3] == ' ':
                    tempvalue = 0
                    if tempvalue > set[3]:
                        totalhw.append(
                            [setgraded[0], 'Homework ' + str(setgraded[1]), setgraded[2], ' ', ' ', ' ', ' '])
                else:
                    getgrade = []
                    cursor = connection.execute('SELECT DISTINCT Hg.grade '
                                                'FROM Students S, Enrolls E, Homeworks H, Homeworks_grade Hg, Enrolls E2, Students S2 '
                                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                                'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND E2.cid = Hg.cid AND E2.sec_no = Hg.sec_no AND E2.semail = S2.semail '
                                                'AND Hg.cid = ?;',
                                                (myid, mypw, setgraded[0]))
                    getgrades = cursor.fetchall()
                    cursor = connection.execute('SELECT DISTINCT Hg.grade '
                                                'FROM Students S, Enrolls E, Homeworks H, Homeworks_grade Hg, Enrolls E2, TA '
                                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                                'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND E2.cid = Hg.cid AND E2.sec_no = Hg.sec_no AND E2.semail = TA.semail '
                                                'AND Hg.cid = ?;',
                                                (myid, mypw, setgraded[0]))
                    getgradet = cursor.fetchall()
                    for set3 in getgrades:
                        if set3[0] == ' ':
                            pass
                        else:
                            getgrade.append(set3[0])
                    for set3 in getgradet:
                        if set3[0] == ' ':
                            pass
                        else:
                            getgrade.append(set3[0])
                    if len(getgrade) == 0:
                        totalhw.append(
                            [setgraded[0], 'Homework ' + str(setgraded[1]), setgraded[2], setgraded[3], ' ', ' ', ' '])
                    else:
                        maxgrade = max(getgrade)
                        mingrade = min(getgrade)
                        avggrade = "{:.2f}".format(
                            sum(getgrade) / len(getgrade))
                        totalhw.append(
                            [setgraded[0], 'Homework ' + str(setgraded[1]), setgraded[2], setgraded[3], mingrade, avggrade,
                             maxgrade])
    for set in hwnotgraded:
        if [set[0], set[1], set[2]] in temphw:
            pass
        else:
            if set[1] == '' and set[2] == '':
                pass
            else:
                totalhw.append(
                    [set[0], 'Homework ' + str(set[1]), set[2], ' ', ' ', ' ', ' '])
    if totalhw:
        return render_template('homework.html', error=error, myhw=totalhw)
    else:
        error = 'invalid input name'
    return render_template('homework.html', error=error)


@app.route('/exam', methods=['POST', 'GET'])
def exam():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT E.cid, Ex.exam_no, Ex.examdesc, ExG.grade '
                                'FROM Students S, Enrolls E, Exams Ex, Exams_grade ExG '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Ex.sec_no AND E.cid = Ex.cid '
                                'AND S.semail = ExG.semail AND E.cid = ExG.cid AND Ex.sec_no = ExG.sec_no AND Ex.exam_no = ExG.exam_no;',
                                (myid, mypw))
    examgraded = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT E.cid, Ex.exam_no, Ex.examdesc '
                                'FROM Students S, Enrolls E, Exams Ex '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Ex.sec_no AND E.cid = Ex.cid;',
                                (myid, mypw))
    examnotgraded = cursor.fetchall()
    setexam = []
    setexam2 = []
    totalexam = []
    tempexam = []
    for set in examgraded:
        setexam.append([set[0], set[1], set[2], set[3]])
    for set in examgraded:
        tempexam.append([set[0], set[1], set[2]])
    for set in examnotgraded:
        setexam2.append([set[0], set[1], set[2], int(-1)])
    for set in setexam2:
        for setgraded in setexam:
            if [setgraded[0], setgraded[1], setgraded[2]] == [set[0], set[1], set[2]]:
                if setgraded[3] == ' ':
                    tempnum = 0
                    if tempnum > set[3]:
                        totalexam.append(
                            [setgraded[0], 'Exam ' + str(setgraded[1]), setgraded[2], ' ', ' ', ' ', ' '])
                else:
                    if setgraded[3] > set[3]:
                        getgrade = []
                        cursor = connection.execute('SELECT DISTINCT Hg.grade '
                                                    'FROM Students S, Enrolls E, Exams H, Exams_grade Hg, Enrolls E2, Students S2 '
                                                    'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                                    'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND E2.cid = Hg.cid AND E2.sec_no = Hg.sec_no AND E2.semail = S2.semail '
                                                    'AND Hg.cid = ?;',
                                                    (myid, mypw, setgraded[0]))
                        getgrades = cursor.fetchall()
                        cursor = connection.execute('SELECT DISTINCT Hg.grade '
                                                    'FROM Students S, Enrolls E, Exams H, Exams_grade Hg, Enrolls E2, TA '
                                                    'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                                    'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND E2.cid = Hg.cid AND E2.sec_no = Hg.sec_no AND E2.semail = TA.semail '
                                                    'AND Hg.cid = ?;',
                                                    (myid, mypw, setgraded[0]))
                        getgradet = cursor.fetchall()
                        for set3 in getgrades:
                            if set3[0] == ' ':
                                pass
                            else:
                                getgrade.append(set3[0])
                        for set3 in getgradet:
                            if set3[0] == ' ':
                                pass
                            else:
                                getgrade.append(set3[0])
                        if len(getgrade) == 0:
                            totalexam.append(
                                [setgraded[0], 'Exam ' + str(setgraded[1]), setgraded[2], setgraded[3], ' ', ' ', ' '])
                        else:
                            maxgrade = max(getgrade)
                            mingrade = min(getgrade)
                            avggrade = "{:.2f}".format(
                                sum(getgrade) / len(getgrade))
                            totalexam.append([setgraded[0], 'Exam ' + str(setgraded[1]),
                                              setgraded[2], setgraded[3], mingrade, avggrade, maxgrade])
    for set in examnotgraded:
        if [set[0], set[1], set[2]] in tempexam:
            pass
        else:
            if set[1] == '' and set[2] == '':
                pass
            else:
                totalexam.append([set[0], 'Exam ' + str(set[1]), set[2], ' '])
    if totalexam:
        return render_template('exam.html', error=error, myexam=totalexam)
    else:
        error = 'invalid input name'
    return render_template('exam.html', error=error)


@app.route('/enroll', methods=['POST', 'GET'])
def Enroll():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT C.cid, C.cname, Sec.sec_no, P.firstname, P.lastname, P.pemail, P.office_num, P.office_building, C.cdesc '
        'FROM Students S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
        'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
        (myid, mypw))
    myschedule = cursor1.fetchall()
    setschedule = []  # append
    for set in myschedule:
        profname = 'Professor ' + set[3] + ' ' + set[4]
        profemail = set[5] + '@Nittanystate.edu'
        setschedule.append([set[0], set[1], set[2], profname,
                            profemail, set[6] + ' ' + set[7], set[8]])
    cursor1 = connection.execute('SELECT cid FROM Courses')
    getcourses = cursor1.fetchall()
    courses = []
    for set in getcourses:
        courses.append(set[0])
    if request.method == 'POST':
        getclass = request.form['course']
        getsection = int(request.form['section'])
        myclass = []
        tempcc = [getclass]
        cursor1 = connection.execute('SELECT Count(*) '
                                     'FROM Enrolls E WHERE E.cid = ? AND E.sec_no = ?', (getclass, getsection))
        numofstuds = cursor1.fetchall()
        numberofstudents = 0
        for set in numofstuds:
            numberofstudents = set[0]
        cursor1 = connection.execute('SELECT Sec.lim '
                                     'FROM Sections Sec WHERE Sec.cid = ? AND Sec.sec_no = ?', (getclass, getsection))
        limitofstuds = cursor1.fetchall()
        limited = 0
        for set in limitofstuds:
            limited = set[0]
        for set in myschedule:
            myclass.append([set[0]])
        if tempcc in myclass:
            global takingnotice
            takingnotice = "You are already taking this course."
            return redirect('/enroll')
        elif numberofstudents >= limited:
            global enrollnotice
            enrollnotice = "The course if full."
            return redirect('/enroll')
        else:
            connection.execute(
                'INSERT INTO Enrolls (semail, cid, sec_no) VALUES (?,?,?)', (myid, getclass, getsection))
            connection.commit()
            cursor1 = connection.execute('SELECT DISTINCT H.hw_no '
                                         'FROM Homeworks H '
                                         'WHERE H.cid = ? AND H.sec_no = ?', (getclass, getsection))
            coursehws = cursor1.fetchall()
            tempnum = ' '
            for set in coursehws:
                connection.execute(
                    'INSERT INTO Homeworks_grade (semail, cid, sec_no, hw_no, grade) VALUES (?,?,?,?,?)', (myid, getclass, getsection, set[0], tempnum))
                connection.commit()

            cursor1 = connection.execute('SELECT DISTINCT E.exam_no '
                                         'FROM Exams E '
                                         'WHERE E.cid = ? AND E.sec_no = ?', (getclass, getsection))
            courseexams = cursor1.fetchall()
            tempnum = ' '
            for set in courseexams:
                connection.execute(
                    'INSERT INTO Exams_grade (semail, cid, sec_no, exam_no, grade) VALUES (?,?,?,?,?)',
                    (myid, getclass, getsection, set[0], tempnum))
                connection.commit()
        return redirect('/course')
    if setschedule:
        return render_template('enrollclass.html', error=error, myschedule=setschedule, courses=courses, notice=enrollnotice, notice2=takingnotice)
    else:
        error = 'invalid input name'
    return render_template('enrollclass.html', error=error)


@app.route('/drop', methods=['POST', 'GET'])
def Drop():
    global enrollnotice
    enrollnotice = ' '
    global takingnotice
    takingnotice = ' '
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT C.cid, C.cname, Sec.sec_no, P.firstname, P.lastname, P.pemail, P.office_num, P.office_building, C.cdesc '
        'FROM Students S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
        'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
        (myid, mypw))
    myschedule = cursor1.fetchall()
    setschedule = []  # append
    for set in myschedule:
        profname = 'Professor ' + set[3] + ' ' + set[4]
        profemail = set[5] + '@Nittanystate.edu'
        setschedule.append([set[0], set[1], set[2], profname,
                            profemail, set[6] + ' ' + set[7], set[8]])
    setschedule = []
    mycourses = []
    for set in myschedule:
        tempname = 'Dr. ' + set[3] + ' ' + set[4]
        setschedule.append([set[0], set[1], set[2], tempname,
                            profemail, set[6] + ' ' + set[7], set[8]])
        mycourses.append(set[0])
    if request.method == 'POST':
        getclass = request.form['course']
        thissemester = 105
        dateTime = datetime.now()
        getyear = int(dateTime.year) - 2000
        getmonth = int(dateTime.month)
        getday = int(dateTime.day)
        getdate = getyear * 10000 + getmonth * 100 + getday
        cursor1 = connection.execute('SELECT S.dropdate '
                                     'FROM Semesters S, Courses C '
                                     'WHERE C.cid = ? AND C.semid = ? AND C.semid = S.semid;',
                                     (getclass, thissemester))
        latedrop = cursor1.fetchall()
        stringtemp = str(latedrop[0][0])
        splitlatedrop = stringtemp.split("/")
        lateyear = int(splitlatedrop[2])
        latemonth = int(splitlatedrop[1])
        lateday = int(splitlatedrop[0])
        latedate = lateyear * 10000 + latemonth * 100 + lateday
        tempnumber = 999999
        if latedate >= getdate:
            connection.execute(
                'DELETE FROM Enrolls WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            connection.execute(
                'DELETE FROM Posts WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            connection.execute(
                'DELETE FROM Comments WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            connection.execute(
                'DELETE FROM Homeworks_grade WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            connection.execute(
                'DELETE FROM Exams_grade WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            return redirect('/course')
        else:
            notice = "The latedrop is passed. You cannot drop this course."
            return render_template('dropclass.html', error=error, myschedule=setschedule, notice=notice, courses=mycourses)
    if setschedule:
        return render_template('dropclass.html', error=error, myschedule=setschedule, courses=mycourses)
    else:
        error = 'invalid input name'
    return render_template('dropclass.html', error=error)


@app.route('/appointment', methods=['POST', 'GET'])
def appointment():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.adate, A.atime, A.title, A.note, A.witheamil '
                                 'FROM Students S, Appointment A, TA '
                                 'WHERE ? = S.semail AND ? = S.password AND S.semail = A.semail ORDER BY A.adate DESC;',
                                 (myid, mypw))
    myappointment = cursor1.fetchall()
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = request.form['date']
        gettime = request.form['time']
        getwith = request.form['email']
        connection.execute(
            'DELETE FROM Appointment WHERE semail = ? AND witheamil = ? AND adate = ? AND atime = ?;', (myid, getwith, getdate, gettime))
        connection.commit()
        return redirect('/appointment')
    if myappointment:
        return render_template('appointment.html', error=error, myappo=myappointment)
    else:
        error = 'invalid input name'
    return render_template('appointment.html', error=error)


@app.route('/newappointment', methods=['POST', 'GET'])
def newappointment():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.adate, A.atime, A.title, A.note, A.witheamil '
                                 'FROM Students S, Appointment A, TA '
                                 'WHERE ? = S.semail AND ? = S.password AND S.semail = A.semail ORDER BY A.adate DESC;',
                                 (myid, mypw))
    myappointment = cursor1.fetchall()
    withwho = []
    cursor1 = connection.execute('SELECT DISTINCT P.firstname, P.lastname '
                                 'FROM Students S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
                                 'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
                                 'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
                                 (myid, mypw))
    myprof = cursor1.fetchall()
    for set in myprof:
        tempname = 'Dr. ' + set[0] + ' ' + set[1]
        withwho.append(tempname)
    if request.method == 'POST':
        cursor1 = connection.execute(
            'SELECT DISTINCT P.pemail, P.firstname, P.lastname FROM Professors P;')
        allprof = cursor1.fetchall()
        getprof = request.form['prof']
        sname = getprof.split(' ')
        print(sname[1] + ' ' + sname[2])
        getpemail = None
        for set in allprof:
            if set[1] == sname[1]:
                if set[2] == sname[2]:
                    getpemail = set[0]
        getnote = request.form['note']
        gettitle = request.form['title']
        getdate = str(request.form['adate'])
        tempdate = getdate.split('-')
        appdate = tempdate[0] + '/' + tempdate[1] + '/' + tempdate[2]
        gettime = str(request.form['atime'])
        connection.execute(
            'INSERT INTO Appointment (semail, adate, atime, note, title, witheamil) VALUES (?,?,?,?,?,?)', (myid, appdate, gettime, getnote, gettitle, getpemail))
        connection.commit()
        return redirect('/appointment')
    if myprof:
        return render_template('newappointment.html', error=error, myappo=myappointment, withwho=withwho)
    else:
        error = 'invalid input name'
    return render_template('newappointment.html', error=error)


forumnum = None
cidnum = None


@app.route('/forum', methods=['POST', 'GET'])
def forum():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.post_no '
                                 'FROM Posts Pt, Students S, Enrolls E, Courses C, Students S2 '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND E.cid = C.cid AND C.cid = Pt.cid AND Pt.semail = S2.semail',
                                 (myid, mypw))
    forum1 = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, TA.firstname, TA.lastname, Pt.post_no '
                                 'FROM Posts Pt, Students S, Enrolls E, Courses C, TA '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND E.cid = C.cid AND C.cid = Pt.cid AND Pt.semail = TA.semail',
                                 (myid, mypw))
    forum2 = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.post_no '
                                 'FROM Posts Pt, Students S, Enrolls E, Courses C, Professors S2 '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND E.cid = C.cid AND C.cid = Pt.cid AND Pt.semail = S2.pemail',
                                 (myid, mypw))
    forum3 = cursor1.fetchall()

    tempforum = []
    for set in forum1:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forum2:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forum3:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    if request.method == 'POST':
        global temppostnum
        temppostnum = request.form['postnum']
        global cidnum
        cidnum = request.form['class']
        return redirect('/comment')
    if forum:
        return render_template('forum.html', error=error, forum=tempforum)
    else:
        error = 'invalid input name'
    return render_template('forum.html', error=error)


@app.route('/createforum', methods=['POST', 'GET'])
def createforum():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT E.cid  '
                                 'FROM Students S, Enrolls E '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail',
                                 (myid, mypw))
    myclass = cursor1.fetchall()
    courses = []
    for set in myclass:
        courses.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getcid = request.form['cid']
        gettitle = request.form['title']
        getnote = request.form['note']
        connection.execute(
            'INSERT INTO Posts (semail, cid, pdate, ptime, ptitle, postdesc) VALUES (?,?,?,?,?,?)', (myid, getcid, getdate, gettime, gettitle, getnote))
        connection.commit()
        return redirect('/forum')
    if myclass:
        return render_template('createforum.html', error=error, myclass=courses)
    else:
        error = 'invalid input name'
    return render_template('createforum.html', error=error)


@app.route('/comment', methods=['POST', 'GET'])
def comment():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
                                 'FROM Posts Pt, Students S, Students S2 '
                                 'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.semail',
                                 (myid, mypw, temppostnum))
    forum = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, Students S, TA S2 '
        'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.semail',
                                (myid, mypw, temppostnum))
    forum1 = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
                                 'FROM Posts Pt, Students S, Professors S2 '
                                 'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.pemail',
                                 (myid, mypw, temppostnum))
    forum2 = cursor1.fetchall()
    print(forum2)
    tempforum = []
    for set in forum:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum1:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum2:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    print(tempforum)
    cursor1 = connection.execute('SELECT DISTINCT Com.pdate, Com.ptime, Students.firstname, Students.lastname, Com.comdesc, Com.post_no '
                                 'FROM Students, Comments Com '
                                 'WHERE ? = Com.post_no AND Com.semail = Students.semail;',
                                 (temppostnum,))
    comment = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Com.pdate, Com.ptime, TA.firstname, TA.lastname, Com.comdesc, Com.post_no '
                                 'FROM TA, Comments Com '
                                 'WHERE ? = Com.post_no AND Com.semail = TA.semail;',
                                 (temppostnum,))
    commentTA = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Com.pdate, Com.ptime, P.firstname, P.lastname, Com.comdesc, Com.post_no '
                                 'FROM Professors P, Comments Com '
                                 'WHERE ? = Com.post_no AND Com.semail = P.pemail;',
                                 (temppostnum,))
    commentP = cursor1.fetchall()
    tempcomment = []
    for set in comment:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    for set in commentTA:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    for set in commentP:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    print(cidnum)
    print(temppostnum)
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")
        getnote = request.form['com']
        connection.execute(
            'INSERT INTO Comments (cid, post_no, pdate, ptime, semail, comdesc) VALUES (?,?,?,?,?,?)',
            (cidnum, temppostnum, getdate, gettime, myid, getnote))
        connection.commit()
        return redirect('/comment')
    if tempforum:
        return render_template('comment.html', error=error, forum=tempforum, comment=tempcomment)
    else:
        error = 'invalid input name'
    return render_template('comment.html', error=error)


@app.route('/inbox', methods=['POST', 'GET'])
def inbox():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, S2.firstname, S2.lastname, M.adate, M.atime, S2.semail '
        'FROM Students S, Message M, Students S2 '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.receiveby AND M.sendby = S2.semail',
        (myid, mypw))
    messageS = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, TA.firstname, TA.lastname, M.adate, M.atime, TA.semail '
        'FROM Students S, Message M, TA '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.receiveby AND M.sendby = TA.semail',
        (myid, mypw))
    messageTA = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, P.firstname, P.lastname, M.adate, M.atime, P.pemail '
        'FROM Students S, Message M, Professors P '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.receiveby AND M.sendby = P.pemail',
        (myid, mypw))
    messageP = cursor1.fetchall()
    tempmess = []
    for set in messageS:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageTA:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageP:
        tempname = 'Dr. ' + set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    if request.method == 'POST':
        global temptitle
        temptitle = request.form['title']
        global tempdate
        tempdate = request.form['date']
        global temptime
        temptime = request.form['time']
        global tempemail
        tempemail = request.form['email']
        global tempflname
        tempflname = request.form['sent']
        return redirect('/readinbox')
    if tempmess:
        return render_template('messageinbox.html', error=error, myinbox=tempmess)
    else:
        error = 'invalid input name'
    return render_template('messageinbox.html', error=error)


@app.route('/sent', methods=['POST', 'GET'])
def sent():
    error = ' '
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, S2.firstname, S2.lastname, M.adate, M.atime, S2.semail '
        'FROM Students S, Message M, Students S2 '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.sendby AND M.receiveby = S2.semail',
        (myid, mypw))
    messageS = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, TA.firstname, TA.lastname, M.adate, M.atime, TA.semail '
        'FROM Students S, Message M, TA '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.sendby AND M.receiveby = TA.semail',
        (myid, mypw))
    messageTA = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, P.firstname, P.lastname, M.adate, M.atime, P.pemail '
        'FROM Students S, Message M, Professors P '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.sendby AND M.receiveby = P.pemail',
        (myid, mypw))
    messageP = cursor1.fetchall()

    tempmess = []
    for set in messageS:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageTA:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageP:
        tempname = 'Dr. ' + set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    if request.method == 'POST':
        global temptitle
        temptitle = request.form['title']
        global tempdate
        tempdate = request.form['date']
        global temptime
        temptime = request.form['time']
        global tempemail
        tempemail = request.form['email']
        global tempflname
        tempflname = request.form['sent']
        return redirect('/readsent')
    if tempmess:
        return render_template('messagesent.html', error=error, mysent=tempmess)
    else:
        error = 'invalid input name'
    return render_template('messagesent.html', error=error)


@app.route('/compost', methods=['POST', 'GET'])
def compost():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT S.semail FROM Students S')
    getStudents = cursor.fetchall()
    cursor = connection.execute('SELECT TA.semail FROM TA')
    getTAs = cursor.fetchall()
    cursor = connection.execute('SELECT P.pemail FROM Professors P')
    getProfessors = cursor.fetchall()
    allMember = []
    for set in getStudents:
        allMember.append(set[0])
    for set in getTAs:
        allMember.append(set[0])
    for set in getProfessors:
        allMember.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getReceiver = request.form['messageto']
        if getReceiver in allMember:
            receiver = getReceiver
            getTitle = request.form['messagetitle']
            getNote = request.form['messagenote']
            connection.execute(
                'INSERT INTO Message(sendby, receiveby, adate, atime, title, note) VALUES (?,?,?,?,?,?);',
                (myid, receiver, getdate, gettime, getTitle, getNote))
            connection.commit()
            return redirect('/inbox')
        else:
            error = "The person you send to is invalid. Please try again."
    return render_template('messagecompost.html', error=error)


@app.route('/readinbox', methods=['POST', 'GET'])
def readinbox():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM Students S, Message M, Students S2 '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = M.receiveby AND S2.semail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessage = cursor.fetchall()
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM Students S, Message M, TA '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = M.receiveby AND TA.semail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessaget = cursor.fetchall()
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM Students S, Message M, Professors P '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = M.receiveby AND P.pemail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessagep = cursor.fetchall()
    message = []
    for set in getmessage:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    for set in getmessaget:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    for set in getmessagep:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    if message:
        return render_template('messageread.html', error=error, message=message)
    else:
        error = "The person you send to is invalid. Please try again."
    return render_template('messageread.html', error=error)


@app.route('/readsent', methods=['POST', 'GET'])
def readsent():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT Distinct M.receiveby, M.adate, M.atime, M.title, M.note '
                                'FROM Students S, Message M '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = M.sendby AND ? = M.receiveby AND ? = M.adate AND ? = M.atime AND ? = M.title',
                                (myid, mypw, tempemail, tempdate, temptime, temptitle))
    getmessage = cursor.fetchall()
    message = []
    for set in getmessage:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    if message:
        return render_template('messageread2.html', error=error, message=message)
    else:
        error = "The person you send to is invalid. Please try again."
    return render_template('messageread2.html', error=error)


tempanum = None
cidanum = None


@app.route('/announcements', methods=['POST', 'GET'])
def announcements():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.anno_no, A.cid, A.ptitle, P.firstname, P.lastname '
                                 'FROM Students S, Enrolls E, Announcements A , Professor_teach Pt, Professors P '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND A.pemail = P.pemail '
                                 'ORDER BY A.anno_no DESC',
                                 (myid, mypw))
    announcements = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT A.anno_no, A.cid, A.ptitle, P.firstname, P.lastname '
                                 'FROM Students S, Enrolls E, Announcements A , TA_teach Pt, TA P '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND A.pemail = P.semail '
                                 'ORDER BY A.anno_no DESC',
                                 (myid, mypw))
    announcementsTA = cursor1.fetchall()
    setannouncements = []
    for set in announcements:
        tempname = set[3] + ' ' + set[4]
        setannouncements.append([set[0], set[1], set[2], tempname])
    for set in announcementsTA:
        tempname = set[3] + ' ' + set[4]
        setannouncements.append([set[0], set[1], set[2], tempname])
    if request.method == 'POST':
        global tempanum
        tempanum = request.form['postnum']
        global cidanum
        cidanum = request.form['class']
        return redirect('/viewannouncements')
    if setannouncements:
        return render_template('announcements.html', error=error, forum=setannouncements)
    else:
        error = 'invalid input name'
    return render_template('announcements.html', error=error)


@app.route('/viewannouncements', methods=['POST', 'GET'])
def viewannouncements():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.cid, A.ptitle, P.firstname, P.lastname, A.postdesc, A.pdate, A.ptime '
                                 'FROM Announcements A, Professors P, Students S, Professor_teach Pt, Sections Sec '
                                 'WHERE ? = S.semail AND ? = S.password AND ? = A.anno_no AND ? = A.cid AND A.cid = Sec.cid AND '
                                 'Sec.teaching_team_id = Pt.teaching_team_id AND Pt.pemail = P.pemail ',
                                 (myid, mypw, tempanum, cidanum))
    forum = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT A.cid, A.ptitle, P.firstname, P.lastname, A.postdesc, A.pdate, A.ptime '
                                 'FROM Announcements A, TA P, Students S, TA_teach Pt, Sections Sec '
                                 'WHERE ? = S.semail AND ? = S.password AND ? = A.anno_no AND ? = A.cid AND A.cid = Sec.cid AND '
                                 'Sec.teaching_team_id = Pt.teaching_team_id AND Pt.semail = P.semail ',
                                 (myid, mypw, tempanum, cidanum))
    forum1 = cursor1.fetchall()
    tempforum = []
    for set in forum:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum1:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    return render_template('viewannouncements.html', error=error, forum=tempforum)


@app.route('/TA', methods=['POST', 'GET'])
def mainTA():
    error = None
    connection = sql.connect('database.db')
    # my info
    cursor = connection.execute(
        'SELECT S.firstname, S.lastname, S.semail, S.age, S.gender, S.major FROM TA S WHERE ? = S.semail AND ? = S.password;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    mygender = None
    if myinfo[0][4] == 'F':
        mygender = 'Female'
    elif myinfo[0][4] == 'M':
        mygender = 'Male'
    changemyinfo = [myinfo[0][0] + ' ' + myinfo[0][1],
                    myinfo[0][2], myinfo[0][3], mygender, myinfo[0][5]]
    setinfo = [(None, None, None, None, None)]
    setinfo[0] = changemyinfo
    # my course
    cursor1 = connection.execute('SELECT C.cid, C.cname, Sec.sec_no, P.firstname, P.lastname, P.pemail, P.office_num, P.office_building '
                                 'FROM TA S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
                                 'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
                                 'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
                                 (myid, mypw))

    myschedule = cursor1.fetchall()
    setschedule = []  # append
    for set in myschedule:
        profname = 'Professor ' + set[3] + ' ' + set[4]
        profemail = set[5] + '@Nittanystate.edu'
        setschedule.append([set[0], set[1], set[2], profname,
                            profemail, set[6] + ' ' + set[7]])
    # my course
    cursor = connection.execute('SELECT E.cid, H.hw_no, H.hwdesc, HG.grade '
                                'FROM TA S, Enrolls E, Homeworks H, Homeworks_grade HG '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = H.sec_no AND E.cid = H.cid '
                                'AND S.semail = HG.semail AND H.cid = HG.cid AND H.sec_no = HG.sec_no AND H.hw_no = HG.hw_no;',
                                (myid, mypw))
    myhwdue = cursor.fetchall()
    cursor = connection.execute('SELECT E.cid, Ex.exam_no, Ex.examdesc, ExG.grade '
                                'FROM TA S, Enrolls E, Exams Ex, Exams_grade ExG '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Ex.sec_no AND E.cid = Ex.cid '
                                'AND S.semail = ExG.semail AND E.cid = ExG.cid AND Ex.sec_no = ExG.sec_no AND Ex.exam_no = ExG.exam_no;',
                                (myid, mypw))
    myexam = cursor.fetchall()
    mydue = []
    for set in myhwdue:
        tempname = 'Homework ' + str(set[1])
        tempset = [set[0], tempname, set[2], set[3]]
        mydue.append(tempset)
    for set in myexam:
        tempname = 'Exam ' + str(set[1])
        tempset = [set[0], tempname, set[2], set[3]]
        mydue.append(tempset)
    if setinfo:
        return render_template('main_TA.html', error=error, myinfo=setinfo, myschedule=setschedule, mydue=mydue)
    else:
        error = 'invalid input name'
    return render_template('main_TA.html', error=error)


@app.route('/profileTA', methods=['POST', 'GET'])
def profileTA():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT S.firstname, S.lastname, S.password, S.semail, S.age, S.gender, S.major, S.phone, S.street, S.zipcode, Ct.city, Ct.state FROM TA S, Zipcodes Z, Cities Ct '
        'WHERE ? = S.semail AND ? = S.password AND Z.zipcode = S.zipcode AND Z.city = Ct.city;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    tempgender = None
    getinfo = []
    for set in myinfo:
        if set[5] == 'F':
            tempgender = 'Female'
        elif set[5] == 'M':
            tempgender = 'Male'
        getinfo.append([set[0], set[1], set[2], set[3], set[4],
                        tempgender, set[6], set[7], set[8], set[9], set[10], set[11]])
    if getinfo:
        return render_template('profileTA.html', error=error, myinfo=getinfo)
    else:
        error = 'invalid input name'
    return render_template('profileTA.html', error=error)


@app.route('/changeprofileTA', methods=['POST', 'GET'])
def changeprofileTA():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT S.firstname, S.lastname, S.password, S.semail, S.age, S.gender, S.major, S.phone, S.street, S.zipcode, Ct.city, Ct.state FROM TA S, Zipcodes Z, Cities Ct '
        'WHERE ? = S.semail AND ? = S.password AND Z.zipcode = S.zipcode AND Z.city = Ct.city;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    getinfo = []
    for set in myinfo:
        if set[5] == 'F':
            tempgender = 'Female'
        elif set[5] == 'M':
            tempgender = 'Male'
        getinfo.append([set[0], set[1], set[2], set[3], set[4],
                        tempgender, set[6], set[7], set[8], set[9], set[10], set[11]])
    if request.method == 'POST':
        getfname = request.form['fname']
        getlname = request.form['lname']
        getstreet = request.form['street']
        getzipcode = int(request.form['zipcode'])
        getcity = request.form['city']
        getstate = request.form['state']
        getphone = request.form['phone']
        connection.execute(
            'UPDATE TA '
            'SET firstname = ?, lastname = ?, street = ?, zipcode = ?, phone = ? '
            'WHERE semail = ? AND password = ?;',
            (getfname, getlname, getstreet, getzipcode, getphone, myid, mypw))
        connection.commit()
        cursor = connection.execute('SELECT Z.zipcode FROM Zipcodes Z;')
        zipcodess = cursor.fetchall()
        zipcodes = []
        for set in zipcodess:
            zipcodes.append(set[0])
        cursor = connection.execute('SELECT C.city FROM Cities C;')
        citiess = cursor.fetchall()
        cities = []
        for set in citiess:
            cities.append(set[0])
        if getzipcode in zipcodes:
            connection.execute(
                'UPDATE Zipcodes '
                'SET city = ? '
                'WHERE zipcode = ?;',
                (getcity, getzipcode))
            connection.commit()
        else:
            connection.execute(
                'INSERT INTO Zipcodes (zipcode, city) VALUES (?,?)', (getzipcode, getcity))
            connection.commit()
        if getcity in cities:
            connection.execute(
                'UPDATE Cities '
                'SET state = ? '
                'WHERE city = ?;',
                (getstate, getcity))
            connection.commit()
        else:
            connection.execute(
                'INSERT INTO Cities (city, state) VALUES (?,?)', (getcity, getstate))
            connection.commit()
        return redirect('/profileTA')
    if getinfo:
        return render_template('changeprofileTA.html', error=error, myinfo=getinfo)
    else:
        error = 'invalid input name'
    return render_template('changeprofileTA.html', error=error)


@app.route('/changepasswordTA', methods=['POST', 'GET'])
def changepasswordTA():
    global mypw
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT S.password FROM TA S '
        'WHERE ? = S.semail AND ? = S.password;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    if request.method == 'POST':
        getoldpw = request.form['oldpw']
        mypwhashed = hashlib.md5()
        mypwhashed.update(getoldpw.encode('utf8'))
        myoldpw = mypwhashed.hexdigest()
        print(myoldpw)
        print(mypw)
        getnewpw = request.form['newpw']
        mynewpwhashed = hashlib.md5()
        mynewpwhashed.update(getnewpw.encode('utf8'))
        mynewpw = mynewpwhashed.hexdigest()
        print(mynewpw)
        if myoldpw == mypw:
            mypw = mynewpw
            print(mypw)
            connection.execute(
                'UPDATE TA '
                'SET password = ?'
                'WHERE semail = ?;',
                (mypw, myid))
            connection.commit()
        else:
            pass
        return redirect('/profileTA')
    if myinfo:
        return render_template('changepasswordTA.html', error=error, myinfo=myinfo)
    else:
        error = 'invalid input name'
    return render_template('changepasswordTA.html', error=error)


@app.route('/classmatesTA', methods=['POST', 'GET'])
def classmatesTA():
    error = None
    connection = sql.connect('database.db')
    getclassmates = []
    cursor = connection.execute(
        'SELECT E2.cid, S2.semail, S2.firstname, S2.lastname, E2.sec_no, S2.age, S2.gender, S2.major '
        'FROM TA S, Enrolls E, Sections Sec, Students S2, Enrolls E2 '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = Sec.cid AND E.sec_no = Sec.sec_no AND E2.cid = Sec.cid AND E2.sec_no = Sec.sec_no AND E2.semail = S2.semail;',
        (myid, mypw))
    myclassmates = cursor.fetchall()
    cursor = connection.execute(
        'SELECT E2.cid, TA.semail, TA.firstname, TA.lastname, E2.sec_no, TA.age, TA.gender, TA.major '
        'FROM TA S, Enrolls E, Sections Sec, TA, Enrolls E2 '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = Sec.cid AND E.sec_no = Sec.sec_no AND E2.cid = Sec.cid AND E2.sec_no = Sec.sec_no AND E2.semail = TA.semail;',
        (myid, mypw))
    myclassmatet = cursor.fetchall()
    for set in myclassmates:
        getclassmates.append(set)
    for set in myclassmatet:
        getclassmates.append(set)
    if myclassmates:
        return render_template('classmatesTA.html', error=error, myclassmates=getclassmates)
    else:
        error = 'invalid input name'
    return render_template('classmatesTA.html', error=error)


@app.route('/courseTA', methods=['POST', 'GET'])
def courseTA():
    global enrollnotice
    enrollnotice = ' '
    global takingnotice
    takingnotice = ' '
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT C.cid, C.cname, Sec.sec_no, P.firstname, P.lastname, P.pemail, P.office_num, P.office_building, C.cdesc '
        'FROM TA S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
        'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
        (myid, mypw))
    myschedule = cursor1.fetchall()
    setschedule = []  # append
    for set in myschedule:
        profname = 'Professor ' + set[3] + ' ' + set[4]
        profemail = set[5] + '@Nittanystate.edu'
        cursor1 = connection.execute('SELECT Hg.grade '
                                     'FROM TA S, Enrolls E, Homeworks H, Homeworks_grade Hg '
                                     'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                     'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no '
                                     'AND Hg.cid = ?;',
                                     (myid, mypw, set[0]))
        myhwgrade = cursor1.fetchall()
        hwgrade = []
        for set2 in myhwgrade:
            hwgrade.append(set2[0])
        cursor = connection.execute('SELECT Hg.grade '
                                    'FROM TA S, Enrolls E, Exams H, Exams_grade Hg '
                                    'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                    'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no '
                                    'AND Hg.cid = ?;',
                                    (myid, mypw, set[0]))
        myexamgrade = cursor.fetchall()
        examgrade = []
        for set2 in myexamgrade:
            examgrade.append(set2[0])
        tempnum = 1
        if len(examgrade) == 0 and len(hwgrade) == 0:
            setschedule.append([set[0], set[1], set[2], profname,
                                profemail, set[6] + ' ' + set[7], set[8], ' '])
        elif len(examgrade) == 0:
            finalgrade = (sum(hwgrade) / len(hwgrade))
            final2deci = "{:.2f}".format(finalgrade)
            setschedule.append([set[0], set[1], set[2], profname,
                                profemail, set[6] + ' ' + set[7], set[8], final2deci])
        elif len(hwgrade) == 0:
            finalgrade = (sum(examgrade) / len(examgrade))
            final2deci = "{:.2f}".format(finalgrade)
            setschedule.append([set[0], set[1], set[2], profname,
                                profemail, set[6] + ' ' + set[7], set[8], final2deci])
        else:
            if ' ' in examgrade or ' ' in hwgrade:
                setschedule.append(
                    [set[0], set[1], set[2], profname, profemail, set[6] + ' ' + set[7], set[8], ' '])
            else:
                finalgrade = (sum(examgrade) / len(examgrade)) * \
                    0.7 + (sum(hwgrade) / len(hwgrade)) * 0.3
                final2deci = "{:.2f}".format(finalgrade)
                setschedule.append([set[0], set[1], set[2], profname,
                                    profemail, set[6] + ' ' + set[7], set[8], final2deci])
    if setschedule:
        return render_template('courseTA.html', error=error, myschedule=setschedule)
    else:
        error = 'invalid input name'
    return render_template('courseTA.html', error=error)


@app.route('/homeworkTA', methods=['POST', 'GET'])
def homeworkTA():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT E.cid, H.hw_no, H.hwdesc, HG.grade '
                                'FROM TA S, Enrolls E, Homeworks H, Homeworks_grade HG '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = H.sec_no AND E.cid = H.cid '
                                'AND S.semail = HG.semail AND H.cid = HG.cid AND H.sec_no = HG.sec_no AND H.hw_no = HG.hw_no;',
                                (myid, mypw))
    hwgraded = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT E.cid, H.hw_no, H.hwdesc '
                                'FROM TA S, Enrolls E, Homeworks H '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = H.sec_no AND E.cid = H.cid;',
                                (myid, mypw))
    hwnotgraded = cursor.fetchall()
    sethw = []
    sethw2 = []
    totalhw = []
    temphw = []
    for set in hwgraded:
        sethw.append([set[0], set[1], set[2], set[3]])
    for set in hwgraded:
        temphw.append([set[0], set[1], set[2]])
    for set in hwnotgraded:
        sethw2.append([set[0], set[1], set[2], int(-1)])
    for set in sethw2:
        for setgraded in sethw:
            if [setgraded[0], setgraded[1], setgraded[2]] == [set[0], set[1], set[2]]:
                if setgraded[3] == ' ':
                    tempvalue = 0
                    if tempvalue > set[3]:
                        totalhw.append(
                            [setgraded[0], 'Homework ' + str(setgraded[1]), setgraded[2], ' ', ' ', ' ', ' '])
                else:
                    getgrade = []
                    cursor = connection.execute('SELECT DISTINCT Hg.grade '
                                                'FROM TA S, Enrolls E, Homeworks H, Homeworks_grade Hg, Enrolls E2, Students S2 '
                                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                                'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND E2.cid = Hg.cid AND E2.sec_no = Hg.sec_no AND E2.semail = S2.semail '
                                                'AND Hg.cid = ?;',
                                                (myid, mypw, setgraded[0]))
                    getgrades = cursor.fetchall()
                    cursor = connection.execute('SELECT DISTINCT Hg.grade '
                                                'FROM TA S, Enrolls E, Homeworks H, Homeworks_grade Hg, Enrolls E2, TA '
                                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                                'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND E2.cid = Hg.cid AND E2.sec_no = Hg.sec_no AND E2.semail = TA.semail '
                                                'AND Hg.cid = ?;',
                                                (myid, mypw, setgraded[0]))
                    getgradet = cursor.fetchall()
                    for set3 in getgrades:
                        if set3[0] == ' ':
                            pass
                        else:
                            getgrade.append(set3[0])
                    for set3 in getgradet:
                        if set3[0] == ' ':
                            pass
                        else:
                            getgrade.append(set3[0])
                    if len(getgrade) == 0:
                        totalhw.append(
                            [setgraded[0], 'Homework ' + str(setgraded[1]), setgraded[2], setgraded[3], ' ', ' ', ' '])
                    else:
                        maxgrade = max(getgrade)
                        mingrade = min(getgrade)
                        avggrade = "{:.2f}".format(
                            sum(getgrade) / len(getgrade))
                        totalhw.append(
                            [setgraded[0], 'Homework ' + str(setgraded[1]), setgraded[2], setgraded[3], mingrade, avggrade,
                             maxgrade])
    for set in hwnotgraded:
        if [set[0], set[1], set[2]] in temphw:
            print([set[0], set[1], set[2]])
            print('okay')  # totalhw.append(set)
        else:
            if set[1] == '' and set[2] == '':
                pass
            else:
                totalhw.append(
                    [set[0], 'Homework ' + str(set[1]), set[2], ' ', ' ', ' ', ' '])
    if totalhw:
        return render_template('homeworkTA.html', error=error, myhw=totalhw)
    else:
        error = 'invalid input name'
    return render_template('homeworkTA.html', error=error)


@app.route('/examTA', methods=['POST', 'GET'])
def examTA():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT E.cid, Ex.exam_no, Ex.examdesc, ExG.grade '
                                'FROM TA S, Enrolls E, Exams Ex, Exams_grade ExG '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Ex.sec_no AND E.cid = Ex.cid '
                                'AND S.semail = ExG.semail AND E.cid = ExG.cid AND Ex.sec_no = ExG.sec_no AND Ex.exam_no = ExG.exam_no;',
                                (myid, mypw))
    examgraded = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT E.cid, Ex.exam_no, Ex.examdesc '
                                'FROM TA S, Enrolls E, Exams Ex '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Ex.sec_no AND E.cid = Ex.cid;',
                                (myid, mypw))
    examnotgraded = cursor.fetchall()
    setexam = []
    setexam2 = []
    totalexam = []
    tempexam = []
    for set in examgraded:
        setexam.append([set[0], set[1], set[2], set[3]])
    for set in examgraded:
        tempexam.append([set[0], set[1], set[2]])
    for set in examnotgraded:
        setexam2.append([set[0], set[1], set[2], int(-1)])
    for set in setexam2:
        for setgraded in setexam:
            if [setgraded[0], setgraded[1], setgraded[2]] == [set[0], set[1], set[2]]:
                if setgraded[3] == ' ':
                    tempnum = 0
                    if tempnum > set[3]:
                        totalexam.append(
                            [setgraded[0], 'Exam ' + str(setgraded[1]), setgraded[2], ' ', ' ', ' ', ' '])
                else:
                    if setgraded[3] > set[3]:
                        getgrade = []
                        cursor = connection.execute('SELECT DISTINCT Hg.grade '
                                                    'FROM TA S, Enrolls E, Exams H, Exams_grade Hg, Enrolls E2, Students S2 '
                                                    'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                                    'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND E2.cid = Hg.cid AND E2.sec_no = Hg.sec_no AND E2.semail = S2.semail '
                                                    'AND Hg.cid = ?;',
                                                    (myid, mypw, setgraded[0]))
                        getgrades = cursor.fetchall()
                        cursor = connection.execute('SELECT DISTINCT Hg.grade '
                                                    'FROM TA S, Enrolls E, Exams H, Exams_grade Hg, Enrolls E2, TA '
                                                    'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.cid = H.cid AND E.sec_no = H.sec_no '
                                                    'AND Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND E2.cid = Hg.cid AND E2.sec_no = Hg.sec_no AND E2.semail = TA.semail '
                                                    'AND Hg.cid = ?;',
                                                    (myid, mypw, setgraded[0]))
                        getgradet = cursor.fetchall()
                        for set3 in getgrades:
                            if set3[0] == ' ':
                                pass
                            else:
                                getgrade.append(set3[0])
                        for set3 in getgradet:
                            if set3[0] == ' ':
                                pass
                            else:
                                getgrade.append(set3[0])
                        print(getgrade)
                        if len(getgrade) == 0:
                            totalexam.append(
                                [setgraded[0], 'Exam ' + str(setgraded[1]), setgraded[2], setgraded[3], ' ', ' ', ' '])
                        else:
                            maxgrade = max(getgrade)
                            mingrade = min(getgrade)
                            avggrade = "{:.2f}".format(
                                sum(getgrade) / len(getgrade))
                            totalexam.append([setgraded[0], 'Exam ' + str(setgraded[1]),
                                              setgraded[2], setgraded[3], mingrade, avggrade, maxgrade])
    for set in examnotgraded:
        if [set[0], set[1], set[2]] in tempexam:
            print([set[0], set[1], set[2]])
            print('okay')  # totalhw.append(set)
        else:
            print([set[0], set[1], set[2]])
            print('not in')
            print([set[0], set[1], set[2], ' '])
            if set[1] == '' and set[2] == '':
                pass
            else:
                totalexam.append([set[0], 'Exam ' + str(set[1]), set[2], ' '])
    if totalexam:
        return render_template('examTA.html', error=error, myexam=totalexam)
    else:
        error = 'invalid input name'
    return render_template('examTA.html', error=error)


@app.route('/enrollTA', methods=['POST', 'GET'])
def EnrollTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT C.cid, C.cname, Sec.sec_no, P.firstname, P.lastname, P.pemail, P.office_num, P.office_building, C.cdesc '
        'FROM TA S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
        'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
        (myid, mypw))
    myschedule = cursor1.fetchall()
    setschedule = []  # append
    for set in myschedule:
        profname = 'Professor ' + set[3] + ' ' + set[4]
        profemail = set[5] + '@Nittanystate.edu'
        setschedule.append([set[0], set[1], set[2], profname,
                            profemail, set[6] + ' ' + set[7], set[8]])
    cursor1 = connection.execute('SELECT cid FROM Courses')
    getcourses = cursor1.fetchall()
    courses = []
    for set in getcourses:
        courses.append(set[0])
    if request.method == 'POST':
        getclass = request.form['course']
        getsection = int(request.form['section'])
        myclass = []
        tempcc = [getclass]
        cursor1 = connection.execute('SELECT Count(*) '
                                     'FROM Enrolls E WHERE E.cid = ? AND E.sec_no = ?', (getclass, getsection))
        numofstuds = cursor1.fetchall()
        numberofstudents = 0
        for set in numofstuds:
            numberofstudents = set[0]
        cursor1 = connection.execute('SELECT Sec.lim '
                                     'FROM Sections Sec WHERE Sec.cid = ? AND Sec.sec_no = ?', (getclass, getsection))
        limitofstuds = cursor1.fetchall()
        limited = 0
        for set in limitofstuds:
            limited = set[0]
        for set in myschedule:
            myclass.append([set[0]])
        print(numberofstudents)
        print(limited)
        if tempcc in myclass:
            global takingnotice
            takingnotice = "You are already taking this course."
            return redirect('/enrollTA')
        elif numberofstudents >= limited:
            global enrollnotice
            enrollnotice = "The course if full."
            return redirect('/enrollTA')
        else:
            connection.execute(
                'INSERT INTO Enrolls (semail, cid, sec_no) VALUES (?,?,?)', (myid, getclass, getsection))
            connection.commit()
            cursor1 = connection.execute('SELECT DISTINCT H.hw_no '
                                         'FROM Homeworks H '
                                         'WHERE H.cid = ? AND H.sec_no = ?', (getclass, getsection))
            coursehws = cursor1.fetchall()
            tempnum = ' '
            for set in coursehws:
                connection.execute(
                    'INSERT INTO Homeworks_grade (semail, cid, sec_no, hw_no, grade) VALUES (?,?,?,?,?)', (myid, getclass, getsection, set[0], tempnum))
                connection.commit()

            cursor1 = connection.execute('SELECT DISTINCT E.exam_no '
                                         'FROM Exams E '
                                         'WHERE E.cid = ? AND E.sec_no = ?', (getclass, getsection))
            courseexams = cursor1.fetchall()
            tempnum = ' '
            for set in courseexams:
                connection.execute(
                    'INSERT INTO Exams_grade (semail, cid, sec_no, exam_no, grade) VALUES (?,?,?,?,?)',
                    (myid, getclass, getsection, set[0], tempnum))
                connection.commit()
        return redirect('/courseTA')
    if setschedule:
        return render_template('enrollclassTA.html', error=error, myschedule=setschedule, courses=courses, notice=enrollnotice, notice2=takingnotice)
    else:
        error = 'invalid input name'
    return render_template('enrollclassTA.html', error=error)


@app.route('/dropTA', methods=['POST', 'GET'])
def DropTA():
    global enrollnotice
    enrollnotice = ' '
    global takingnotice
    takingnotice = ' '
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT C.cid, C.cname, Sec.sec_no, P.firstname, P.lastname, P.pemail, P.office_num, P.office_building, C.cdesc '
        'FROM TA S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
        'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
        'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
        (myid, mypw))
    myschedule = cursor1.fetchall()
    setschedule = []  # append
    for set in myschedule:
        profname = 'Professor ' + set[3] + ' ' + set[4]
        profemail = set[5] + '@Nittanystate.edu'
        setschedule.append([set[0], set[1], set[2], profname,
                            profemail, set[6] + ' ' + set[7], set[8]])
    setschedule = []
    mycourses = []
    for set in myschedule:
        tempname = 'Dr. ' + set[3] + ' ' + set[4]
        setschedule.append([set[0], set[1], set[2], tempname,
                            profemail, set[6] + ' ' + set[7], set[8]])
        mycourses.append(set[0])
    print(mycourses)
    if request.method == 'POST':
        getclass = request.form['course']
        thissemester = 105
        dateTime = datetime.now()
        getyear = int(dateTime.year) - 2000
        getmonth = int(dateTime.month)
        getday = int(dateTime.day)
        getdate = getyear * 10000 + getmonth * 100 + getday
        cursor1 = connection.execute('SELECT S.dropdate '
                                     'FROM Semesters S, Courses C '
                                     'WHERE C.cid = ? AND C.semid = ? AND C.semid = S.semid;',
                                     (getclass, thissemester))
        latedrop = cursor1.fetchall()
        stringtemp = str(latedrop[0][0])
        splitlatedrop = stringtemp.split("/")
        lateyear = int(splitlatedrop[2])
        latemonth = int(splitlatedrop[1])
        lateday = int(splitlatedrop[0])
        latedate = lateyear * 10000 + latemonth * 100 + lateday
        tempnumber = 999999
        if latedate >= getdate:
            connection.execute(
                'DELETE FROM Enrolls WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            connection.execute(
                'DELETE FROM Posts WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            connection.execute(
                'DELETE FROM Comments WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            connection.execute(
                'DELETE FROM Homeworks_grade WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            connection.execute(
                'DELETE FROM Exams_grade WHERE cid = ? AND semail = ?;', (getclass, myid))
            connection.commit()
            return redirect('/courseTA')
        else:
            notice = "The latedrop is passed. You cannot drop this course."
            return render_template('dropclassTA.html', error=error, myschedule=setschedule, notice=notice, courses=mycourses)
    if setschedule:
        return render_template('dropclassTA.html', error=error, myschedule=setschedule, courses=mycourses)
    else:
        error = 'invalid input name'
    return render_template('dropclassTA.html', error=error)


@app.route('/appointmentTA', methods=['POST', 'GET'])
def appointmentTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.adate, A.atime, A.title, A.note, A.witheamil '
                                 'FROM TA S, Appointment A, TA '
                                 'WHERE ? = S.semail AND ? = S.password AND S.semail = A.semail ORDER BY A.adate DESC;',
                                 (myid, mypw))
    myappointment = cursor1.fetchall()
    if request.method == 'POST':
        dateTime = datetime.now()
        getDate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        getdate = request.form['date']
        gettime = request.form['time']
        getwith = request.form['email']
        connection.execute(
            'DELETE FROM Appointment WHERE semail = ? AND witheamil = ? AND adate = ? AND atime = ?;', (myid, getwith, getdate, gettime))
        connection.commit()
        return redirect('/appointmentTA')
    if myappointment:
        return render_template('appointmentTA.html', error=error, myappo=myappointment)
    else:
        error = 'invalid input name'
    return render_template('appointmentTA.html', error=error)


@app.route('/newappointmentTA', methods=['POST', 'GET'])
def newappointmentTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.adate, A.atime, A.title, A.note, A.witheamil '
                                 'FROM TA S, Appointment A, TA '
                                 'WHERE ? = S.semail AND ? = S.password AND S.semail = A.semail ORDER BY A.adate DESC;',
                                 (myid, mypw))
    myappointment = cursor1.fetchall()
    withwho = []
    cursor1 = connection.execute('SELECT DISTINCT P.firstname, P.lastname '
                                 'FROM TA S, Enrolls E, Sections Sec, Courses C, Professor_teach PT, Professors P '
                                 'WHERE ? = S.semail AND ? = S.password AND S.semail = E.semail AND E.sec_no = Sec.sec_no '
                                 'AND Sec.cid = C.cid AND C.cid = E.cid AND Sec.Teaching_team_id = PT.Teaching_team_id AND PT.pemail = P.pemail;',
                                 (myid, mypw))
    myprof = cursor1.fetchall()
    for set in myprof:
        tempname = 'Dr. ' + set[0] + ' ' + set[1]
        withwho.append(tempname)
    if request.method == 'POST':
        cursor1 = connection.execute(
            'SELECT DISTINCT P.pemail, P.firstname, P.lastname FROM Professors P;')
        allprof = cursor1.fetchall()
        getprof = request.form['prof']
        sname = getprof.split(' ')
        print(sname[1] + ' ' + sname[2])
        getpemail = None
        for set in allprof:
            if set[1] == sname[1]:
                if set[2] == sname[2]:
                    getpemail = set[0]
        getnote = request.form['note']
        gettitle = request.form['title']
        getdate = str(request.form['adate'])
        tempdate = getdate.split('-')
        appdate = tempdate[0] + '/' + tempdate[1] + '/' + tempdate[2]
        gettime = str(request.form['atime'])
        connection.execute(
            'INSERT INTO Appointment (semail, adate, atime, note, title, witheamil) VALUES (?,?,?,?,?,?)', (myid, appdate, gettime, getnote, gettitle, getpemail))
        connection.commit()
        return redirect('/appointmentTA')
    if myprof:
        return render_template('newappointmentTA.html', error=error, myappo=myappointment, withwho=withwho)
    else:
        error = 'invalid input name'
    return render_template('newappointmentTA.html', error=error)


@app.route('/forumTA', methods=['POST', 'GET'])
def forumTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.post_no '
                                 'FROM Posts Pt, TA S, Enrolls E, Courses C, Students S2 '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND E.cid = C.cid AND C.cid = Pt.cid AND Pt.semail = S2.semail',
                                 (myid, mypw))
    forum1 = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, TA.firstname, TA.lastname, Pt.post_no '
                                 'FROM Posts Pt, TA S, Enrolls E, Courses C, TA '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND E.cid = C.cid AND C.cid = Pt.cid AND Pt.semail = TA.semail',
                                 (myid, mypw))
    forum2 = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.post_no '
                                 'FROM Posts Pt, TA S, Enrolls E, Courses C, Professors S2 '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND E.cid = C.cid AND C.cid = Pt.cid AND Pt.semail = S2.pemail',
                                 (myid, mypw))
    forum3 = cursor1.fetchall()

    tempforum = []
    for set in forum1:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forum2:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forum3:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    if request.method == 'POST':
        global temppostnum
        temppostnum = request.form['postnum']
        global cidnum
        cidnum = request.form['class']
        return redirect('/commentTA')
    if forum:
        return render_template('forumTA.html', error=error, forum=tempforum)
    else:
        error = 'invalid input name'
    return render_template('forumTA.html', error=error)


@app.route('/createforumTA', methods=['POST', 'GET'])
def createforumTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT E.cid  '
                                 'FROM TA S, Enrolls E '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail',
                                 (myid, mypw))
    myclass = cursor1.fetchall()
    courses = []
    for set in myclass:
        courses.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getcid = request.form['cid']
        gettitle = request.form['title']
        getnote = request.form['note']
        connection.execute(
            'INSERT INTO Posts (semail, cid, pdate, ptime, ptitle, postdesc) VALUES (?,?,?,?,?,?)', (myid, getcid, getdate, gettime, gettitle, getnote))
        connection.commit()
        return redirect('/forumTA')
    if myclass:
        return render_template('createforumTA.html', error=error, myclass=courses)
    else:
        error = 'invalid input name'
    return render_template('createforumTA.html', error=error)


@app.route('/commentTA', methods=['POST', 'GET'])
def commentTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
                                 'FROM Posts Pt, TA S, Enrolls E, Courses C, Students S2 '
                                 'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND S.semail = E.semail AND E.cid = C.cid AND C.cid = Pt.cid AND Pt.semail = S2.semail',
                                 (myid, mypw, temppostnum))
    forum = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, TA S, TA S2 '
        'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.semail',
        (myid, mypw, temppostnum))
    forum1 = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, TA S, Professors S2 '
        'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.pemail',
        (myid, mypw, temppostnum))
    forum2 = cursor1.fetchall()
    print(forum2)
    tempforum = []
    for set in forum:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum1:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum2:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])

    cursor1 = connection.execute('SELECT DISTINCT Com.pdate, Com.ptime, Students.firstname, Students.lastname, Com.comdesc, Com.post_no '
                                 'FROM Students, Comments Com '
                                 'WHERE ? = Com.post_no AND Com.semail = Students.semail;',
                                 (temppostnum,))
    comment = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Com.pdate, Com.ptime, TA.firstname, TA.lastname, Com.comdesc, Com.post_no '
                                 'FROM TA, Comments Com '
                                 'WHERE ? = Com.post_no AND Com.semail = TA.semail;',
                                 (temppostnum,))
    commentTA = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT Com.pdate, Com.ptime, P.firstname, P.lastname, Com.comdesc, Com.post_no '
                                 'FROM Professors P, Comments Com '
                                 'WHERE ? = Com.post_no AND Com.semail = P.pemail;',
                                 (temppostnum,))
    commentP = cursor1.fetchall()
    tempcomment = []
    for set in comment:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    for set in commentTA:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    for set in commentP:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    print(cidnum)
    print(temppostnum)
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")
        getnote = request.form['com']
        connection.execute(
            'INSERT INTO Comments (cid, post_no, pdate, ptime, semail, comdesc) VALUES (?,?,?,?,?,?)',
            (cidnum, temppostnum, getdate, gettime, myid, getnote))
        connection.commit()
        return redirect('/commentTA')
    if tempforum:
        return render_template('commentTA.html', error=error, forum=tempforum, comment=tempcomment)
    else:
        error = 'invalid input name'
    return render_template('commentTA.html', error=error)


@app.route('/inboxTA', methods=['POST', 'GET'])
def inboxTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, S2.firstname, S2.lastname, M.adate, M.atime, S2.semail '
        'FROM TA S, Message M, Students S2 '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.receiveby AND M.sendby = S2.semail',
        (myid, mypw))
    messageS = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, TA.firstname, TA.lastname, M.adate, M.atime, TA.semail '
        'FROM TA S, Message M, TA '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.receiveby AND M.sendby = TA.semail',
        (myid, mypw))
    messageTA = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, P.firstname, P.lastname, M.adate, M.atime, P.pemail '
        'FROM TA S, Message M, Professors P '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.receiveby AND M.sendby = P.pemail',
        (myid, mypw))
    messageP = cursor1.fetchall()
    tempmess = []
    for set in messageS:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageTA:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageP:
        tempname = 'Dr. ' + set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    if request.method == 'POST':
        global temptitle
        temptitle = request.form['title']
        global tempdate
        tempdate = request.form['date']
        global temptime
        temptime = request.form['time']
        global tempemail
        tempemail = request.form['email']
        global tempflname
        tempflname = request.form['sent']
        return redirect('/readinboxTA')
    if tempmess:
        return render_template('messageinboxTA.html', error=error, myinbox=tempmess)
    else:
        error = 'invalid input name'
    return render_template('messageinboxTA.html', error=error)


@app.route('/sentTA', methods=['POST', 'GET'])
def sentTA():
    error = ' '
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, S2.firstname, S2.lastname, M.adate, M.atime, S2.semail '
        'FROM TA S, Message M, Students S2 '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.sendby AND M.receiveby = S2.semail',
        (myid, mypw))
    messageS = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, TA.firstname, TA.lastname, M.adate, M.atime, TA.semail '
        'FROM TA S, Message M, TA '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.sendby AND M.receiveby = TA.semail',
        (myid, mypw))
    messageTA = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, P.firstname, P.lastname, M.adate, M.atime, P.pemail '
        'FROM TA S, Message M, Professors P '
        'WHERE ? = S.semail AND ? = S.Password AND S.semail = M.sendby AND M.receiveby = P.pemail',
        (myid, mypw))
    messageP = cursor1.fetchall()

    tempmess = []
    for set in messageS:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageTA:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageP:
        tempname = 'Dr. ' + set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    if request.method == 'POST':
        global temptitle
        temptitle = request.form['title']
        global tempdate
        tempdate = request.form['date']
        global temptime
        temptime = request.form['time']
        global tempemail
        tempemail = request.form['email']
        global tempflname
        tempflname = request.form['sent']
        return redirect('/readsentTA')
    if tempmess:
        return render_template('messagesentTA.html', error=error, mysent=tempmess)
    else:
        error = 'invalid input name'
    return render_template('messagesentTA.html', error=error)


@app.route('/compostTA', methods=['POST', 'GET'])
def compostTA():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT S.semail FROM Students S')
    getStudents = cursor.fetchall()
    cursor = connection.execute('SELECT TA.semail FROM TA')
    getTAs = cursor.fetchall()
    cursor = connection.execute('SELECT P.pemail FROM Professors P')
    getProfessors = cursor.fetchall()
    allMember = []
    for set in getStudents:
        allMember.append(set[0])
    for set in getTAs:
        allMember.append(set[0])
    for set in getProfessors:
        allMember.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getReceiver = request.form['messageto']
        if getReceiver in allMember:
            receiver = getReceiver
            getTitle = request.form['messagetitle']
            getNote = request.form['messagenote']
            connection.execute(
                'INSERT INTO Message(sendby, receiveby, adate, atime, title, note) VALUES (?,?,?,?,?,?);',
                (myid, receiver, getdate, gettime, getTitle, getNote))
            connection.commit()
            return redirect('/inboxTA')
        else:
            error = "The person you send to is invalid. Please try again."
    return render_template('messagecompostTA.html', error=error)


@app.route('/readinboxTA', methods=['POST', 'GET'])
def readinboxTA():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM TA S, Message M, Students S2 '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = M.receiveby AND S2.semail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessage = cursor.fetchall()
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM TA S, Message M, TA '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = M.receiveby AND TA.semail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessaget = cursor.fetchall()
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM TA S, Message M, Professors P '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = M.receiveby AND P.pemail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessagep = cursor.fetchall()
    message = []
    for set in getmessage:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    for set in getmessaget:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    for set in getmessagep:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    if message:
        return render_template('messagereadTA.html', error=error, message=message)
    else:
        error = "The person you send to is invalid. Please try again."
    return render_template('messagereadTA.html', error=error)


@app.route('/readsentTA', methods=['POST', 'GET'])
def readsentTA():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT Distinct M.receiveby, M.adate, M.atime, M.title, M.note '
                                'FROM TA S, Message M '
                                'WHERE ? = S.semail AND ? = S.password AND S.semail = M.sendby AND ? = M.receiveby AND ? = M.adate AND ? = M.atime AND ? = M.title',
                                (myid, mypw, tempemail, tempdate, temptime, temptitle))
    getmessage = cursor.fetchall()
    message = []
    for set in getmessage:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    if message:
        return render_template('messageread2TA.html', error=error, message=message)
    else:
        error = "The person you send to is invalid. Please try again."
    return render_template('messageread2TA.html', error=error)


@app.route('/announcementsTA', methods=['POST', 'GET'])
def announcementsTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.anno_no, A.cid, A.ptitle, P.firstname, P.lastname '
                                 'FROM TA S, Enrolls E, Announcements A , Professor_teach Pt, Professors P '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND A.pemail = P.pemail '
                                 'ORDER BY A.anno_no DESC',
                                 (myid, mypw))
    announcements = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT A.anno_no, A.cid, A.ptitle, P.firstname, P.lastname '
                                 'FROM TA S, Enrolls E, Announcements A , TA_teach Pt, TA P '
                                 'WHERE ? = S.semail AND ? = S.Password AND S.semail = E.semail AND A.pemail = P.semail '
                                 'ORDER BY A.anno_no DESC',
                                 (myid, mypw))
    announcementsTA = cursor1.fetchall()
    setannouncements = []
    for set in announcements:
        tempname = set[3] + ' ' + set[4]
        setannouncements.append([set[0], set[1], set[2], tempname])
    for set in announcementsTA:
        tempname = set[3] + ' ' + set[4]
        setannouncements.append([set[0], set[1], set[2], tempname])
    if request.method == 'POST':
        global tempanum
        tempanum = request.form['postnum']
        global cidanum
        cidanum = request.form['class']
        return redirect('/viewannouncements')
    if setannouncements:
        return render_template('announcementsTA.html', error=error, forum=setannouncements)
    else:
        error = 'invalid input name'
    return render_template('announcementsTA.html', error=error)


@app.route('/viewannouncementsTA', methods=['POST', 'GET'])
def viewannouncementsTA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.cid, A.ptitle, P.firstname, P.lastname, A.postdesc, A.pdate, A.ptime '
                                 'FROM Announcements A, Professors P, TA S, Professor_teach Pt, Sections Sec '
                                 'WHERE ? = S.semail AND ? = S.password AND ? = A.anno_no AND ? = A.cid AND A.cid = Sec.cid AND '
                                 'Sec.teaching_team_id = Pt.teaching_team_id AND Pt.pemail = P.pemail ',
                                 (myid, mypw, tempanum, cidanum))
    forum = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT A.cid, A.ptitle, P.firstname, P.lastname, A.postdesc, A.pdate, A.ptime '
                                 'FROM Announcements A, TA P, TA S, TA_teach Pt, Sections Sec '
                                 'WHERE ? = S.semail AND ? = S.password AND ? = A.anno_no AND ? = A.cid AND A.cid = Sec.cid AND '
                                 'Sec.teaching_team_id = Pt.teaching_team_id AND Pt.semail = P.semail ',
                                 (myid, mypw, tempanum, cidanum))
    forum2 = cursor1.fetchall()
    tempforum = []
    for set in forum:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum2:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    return render_template('viewannouncementsTA.html', error=error, forum=tempforum)


@app.route('/announcementsP', methods=['POST', 'GET'])
def announcementsP():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.anno_no, A.cid, A.ptitle, P.firstname, P.lastname '
                                 'FROM Announcements A , Professor_teach Pt, Professors P, Sections Sec '
                                 'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = Pt.pemail AND Pt.teaching_team_id = Sec.teaching_team_id AND Sec.cid = A.cid '
                                 'ORDER BY A.anno_no DESC',
                                 (myid, mypw))
    announcements = cursor1.fetchall()
    cursor1 = connection.execute('SELECT DISTINCT A.anno_no, A.cid, A.ptitle, TA.firstname, TA.lastname '
                                 'FROM Announcements A , Professor_teach Pt, Professors P, Sections Sec, TA '
                                 'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = Pt.pemail AND Pt.teaching_team_id = Sec.teaching_team_id AND Sec.cid = A.cid '
                                 'AND A.pemail = TA.semail '
                                 'ORDER BY A.anno_no DESC',
                                 (myid, mypw))
    announcementsTA = cursor1.fetchall()
    setannouncements = []
    for set in announcements:
        tempname = set[3] + ' ' + set[4]
        setannouncements.append([set[0], set[1], set[2], tempname])
    for set in announcementsTA:
        tempname = set[3] + ' ' + set[4]
        setannouncements.append([set[0], set[1], set[2], tempname])
    if request.method == 'POST':
        global tempanum
        tempanum = request.form['postnum']
        global cidanum
        cidanum = request.form['class']
        return redirect('/viewannouncementsP')
    if setannouncements:
        return render_template('announcementsP.html', error=error, forum=setannouncements)
    else:
        error = 'invalid input name'
    return render_template('announcementsP.html', error=error)


@app.route('/createannouncementsP', methods=['POST', 'GET'])
def createannouncementsP():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT Sec.cid  '
                                 'FROM Professors P, Professor_teach Pt, Sections Sec '
                                 'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = Pt.pemail AND Pt.teaching_team_id = Sec.teaching_team_id ',
                                 (myid, mypw))
    myclass = cursor1.fetchall()
    courses = []
    for set in myclass:
        courses.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getcid = request.form['cid']
        gettitle = request.form['title']
        getnote = request.form['note']
        connection.execute(
            'INSERT INTO Announcements (cid, pdate, ptime, ptitle, pemail, postdesc) VALUES (?,?,?,?,?,?)', (getcid, getdate, gettime, gettitle, myid, getnote))
        connection.commit()
        return redirect('/announcementsP')
    if myclass:
        return render_template('createannouncementsP.html', error=error, myclass=courses)
    else:
        error = 'invalid input name'
    return render_template('createannouncementsP.html', error=error)


@app.route('/viewannouncementsP', methods=['POST', 'GET'])
def viewannouncementsP():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.cid, A.ptitle, P.firstname, P.lastname, A.postdesc, A.pdate, A.ptime '
                                 'FROM Announcements A, Professors P '
                                 'WHERE ? = P.pemail AND ? = P.Password AND ? = A.anno_no AND ? = A.cid ',
                                 (myid, mypw, tempanum, cidanum))
    forum = cursor1.fetchall()
    tempforum = []
    for set in forum:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    return render_template('viewannouncementsP.html', error=error, forum=tempforum)


@app.route('/professor', methods=['POST', 'GET'])
def professor():
    error = None
    connection = sql.connect('database.db')
    # my info
    cursor = connection.execute(
        'SELECT P.firstname, P.lastname, P.pemail, P.age, P.gender, P.title FROM Professors P WHERE ? = P.pemail AND ? = P.password;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    mygender = None
    if myinfo[0][4] == 'F':
        mygender = 'Female'
    elif myinfo[0][4] == 'M':
        mygender = 'Male'
    changemyinfo = [myinfo[0][0] + ' ' + myinfo[0][1],
                    myinfo[0][2], myinfo[0][3], mygender, myinfo[0][5]]
    setinfo = [(None, None, None, None, None)]
    setinfo[0] = changemyinfo
    # my Students
    cursor = connection.execute('SELECT Sec.cid, S.firstname, S.lastname, Sec.sec_no, S.age, S.gender, S.major '
                                'FROM Students S, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail ORDER BY S.lastname ASC LIMIT 5',
                                (myid, mypw))
    mystudents = cursor.fetchall()
    setstudent = []  # append
    for set in mystudents:
        gen = None
        if set[5] == 'F':
            gen = 'Female'
        elif set[5] == 'M':
            gen = 'Male'
        tempstudents = set[1] + ' ' + set[2]
        setstudent.append([set[0], tempstudents, set[3], set[4], gen, set[6]])
    # my coming up
    cursor = connection.execute('SELECT DISTINCT H.cid, H.hw_no, H.hwdesc '
                                'FROM Professors P, Professor_teach PT, Sections Sec, Homeworks H '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.sec_no = H.sec_no AND Sec.cid = H.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;',
                                (myid, mypw))
    hwdue = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT Ex.cid, Ex.exam_no, Ex.examdesc '
                                'FROM Professors P, Professor_teach PT, Sections Sec, Exams Ex '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.sec_no = Ex.sec_no AND Sec.cid = Ex.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;',
                                (myid, mypw))
    exam = cursor.fetchall()
    mydue = []
    for set in hwdue:
        tempname = 'Homework ' + str(set[1])
        tempset = [set[0], tempname, set[2]]
        mydue.append(tempset)
    for set in exam:
        tempname = 'Exam ' + str(set[1])
        tempset = [set[0], tempname, set[2]]
        mydue.append(tempset)
    if setinfo:
        return render_template('main_professor.html', error=error, myinfo=setinfo, mystudent=setstudent,
                               mydue=mydue)
    else:
        error = 'invalid input name'
    return render_template('main_professor.html', error=error)


@app.route('/profileP', methods=['POST', 'GET'])
def profileP():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT P.firstname, P.lastname, P.password, P.pemail, P.age, P.gender, P.office_building, P.office_num, D.dname, P.title FROM Professors P, Departments D '
        'WHERE ? = P.pemail AND ? = P.password AND P.did = D.did;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    mygender = None
    if myinfo[0][5] == 'F':
        mygender = 'Female'
    elif myinfo[0][5] == 'M':
        mygender = 'Male'
    myoffice = myinfo[0][6] + ' ' + myinfo[0][7]
    mydept = myinfo[0][8] + ': ' + myinfo[0][9]
    setinfo = [[myinfo[0][0], myinfo[0][1], myinfo[0][2],
                myinfo[0][3], myinfo[0][4], mygender, myoffice, mydept]]
    print(setinfo)
    if setinfo:
        return render_template('profileP.html', error=error, myinfo=setinfo)
    else:
        error = 'invalid input name'
    return render_template('profileP.html', error=error)


@app.route('/changeprofileP', methods=['POST', 'GET'])
def changeprofileP():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT P.firstname, P.lastname, P.password, P.pemail, P.age, P.gender, P.office_building, P.office_num FROM Professors P, Departments D '
        'WHERE ? = P.pemail AND ? = P.password AND P.did = D.did;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    mygender = None
    if myinfo[0][5] == 'F':
        mygender = 'Female'
    elif myinfo[0][5] == 'M':
        mygender = 'Male'
    getinfo = [[myinfo[0][0], myinfo[0][1], myinfo[0][2], myinfo[0]
                [3], myinfo[0][4], mygender, myinfo[0][6], myinfo[0][7]]]
    if request.method == 'POST':
        getfname = request.form['fname']
        getlname = request.form['lname']
        getofficebuild = request.form['office_build']
        getofficenum = request.form['office_num']
        connection.execute(
            'UPDATE Professors '
            'SET firstname = ?, lastname = ?, office_building = ?, office_num = ? '
            'WHERE pemail = ? AND password = ?;',
            (getfname, getlname, getofficebuild, getofficenum, myid, mypw))
        connection.commit()
        return redirect('/profileP')
    if getinfo:
        return render_template('changeprofileP.html', error=error, myinfo=getinfo)
    else:
        error = 'invalid input name'
    return render_template('changeprofileP.html', error=error)


@app.route('/changepasswordP', methods=['POST', 'GET'])
def changepasswordP():
    global mypw
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute(
        'SELECT P.password FROM Professors P '
        'WHERE ? = P.pemail AND ? = P.password;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    if request.method == 'POST':
        getoldpw = request.form['oldpw']
        mypwhashed = hashlib.md5()
        mypwhashed.update(getoldpw.encode('utf8'))
        myoldpw = mypwhashed.hexdigest()
        print(myoldpw)
        print(mypw)
        getnewpw = request.form['newpw']
        mynewpwhashed = hashlib.md5()
        mynewpwhashed.update(getnewpw.encode('utf8'))
        mynewpw = mynewpwhashed.hexdigest()
        print(mynewpw)
        if myoldpw == mypw:
            mypw = mynewpw
            print(mypw)
            connection.execute(
                'UPDATE Professors '
                'SET password = ?'
                'WHERE pemail = ?;',
                (mypw, myid))
            connection.commit()
        else:
            pass
        return redirect('/profileP')
    if myinfo:
        return render_template('changepasswordP.html', error=error, myinfo=myinfo)
    else:
        error = 'invalid input name'
    return render_template('changepasswordP.html', error=error)


@app.route('/studentsP', methods=['POST', 'GET'])
def mystudents():
    error = None
    connection = sql.connect('database.db')
    allstud = []
    cursor = connection.execute('SELECT Sec.cid, S.firstname, S.lastname, Sec.sec_no, S.age, S.gender, S.major '
                                'FROM Students S, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail ORDER BY S.lastname',
                                (myid, mypw))
    mystudents = cursor.fetchall()
    cursor = connection.execute('SELECT Sec.cid, TA.firstname, TA.lastname, Sec.sec_no, TA.age, TA.gender, TA.major '
                                'FROM TA, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND TA.semail = E.semail ORDER BY TA.lastname',
                                (myid, mypw))
    mystudentt = cursor.fetchall()
    for set in mystudents:
        gen = None
        if set[5] == 'F':
            gen = 'Female'
        elif set[5] == 'M':
            gen = 'Male'
        tempstudents = set[1] + ' ' + set[2]
        allstud.append([set[0], tempstudents, set[3], set[4], gen, set[6]])
    for set in mystudentt:
        gen = None
        if set[5] == 'F':
            gen = 'Female'
        elif set[5] == 'M':
            gen = 'Male'
        tempstudents = set[1] + ' ' + set[2]
        allstud.append([set[0], tempstudents, set[3], set[4], gen, set[6]])
    if allstud:
        return render_template('studentsP.html', error=error, allstud=allstud)
    else:
        error = 'invalid input name'
    return render_template('studentsP.html', error=error)


@app.route('/homeworkP', methods=['POST', 'GET'])
def homeworkP():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT H.cid, H.sec_no, H.hw_no, H.hwdesc '
                                'FROM Professors P, Professor_teach PT, Sections Sec, Homeworks H '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.sec_no = H.sec_no AND Sec.cid = H.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;', (myid, mypw))
    hwdue = cursor.fetchall()
    sethw = []
    for set in hwdue:
        tempname = 'Homework ' + str(set[2])
        sethw.append([set[0], set[1], tempname, set[3]])
    if request.method == 'POST':
        global tempcourse
        tempcourse = request.form['class']
        global tempsection
        tempsection = request.form['sec']
        global temphomework
        temphomework = request.form['homework']
        global temphwdesc
        temphwdesc = request.form['hwdesc']
        return redirect('/homeworkGradeP')
    if sethw:
        return render_template('homeworkP.html', error=error, hwdue=sethw)
    else:
        error = 'invalid input name'
    return render_template('homeworkP.html', error=error)


@app.route('/homeworkGradeP', methods=['POST', 'GET'])
def homeworkGradeP():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT S.firstname, S.lastname, S.semail, Sec.cid, Sec.sec_no, H.hw_no, Hg.grade '
                                'FROM Professors P, Professor_teach Pt, Sections Sec, Enrolls E, Homeworks H, Students S, Homeworks_grade Hg '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail AND H.cid = E.cid AND H.sec_no = E.sec_no AND '
                                'Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND Hg.hw_no = H.hw_no AND Hg.semail = E.semail AND '
                                '? = Sec.cid AND ? = Sec.sec_no AND ? = H.hwdesc;',
                                (myid, mypw, tempcourse, tempsection, temphwdesc))
    studenthw = cursor.fetchall()
    cursor = connection.execute('SELECT TA.firstname, TA.lastname, TA.semail, Sec.cid, Sec.sec_no, H.hw_no, Hg.grade '
                                'FROM Professors P, Professor_teach Pt, Sections Sec, Enrolls E, Homeworks H, TA, Homeworks_grade Hg '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND TA.semail = E.semail AND H.cid = E.cid AND H.sec_no = E.sec_no AND '
                                'Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND Hg.hw_no = H.hw_no AND Hg.semail = E.semail AND '
                                '? = Sec.cid AND ? = Sec.sec_no AND ? = H.hwdesc;', (myid, mypw, tempcourse, tempsection, temphwdesc))
    TAhw = cursor.fetchall()
    sethw = []  # append
    for set in studenthw:
        tempstudents = set[0] + ' ' + set[1]
        tempemail = set[2] + '@Nittanystate.edu'
        tempname = 'Homework ' + str(set[5])
        sethw.append([tempstudents, tempemail, set[3],
                      set[4], tempname, set[6]])
    for set in TAhw:
        tempstudents = set[0] + ' ' + set[1]
        tempemail = set[2] + '@Nittanystate.edu'
        tempname = 'Homework ' + str(set[5])
        sethw.append([tempstudents, tempemail, set[3],
                      set[4], tempname, set[6]])
    if request.method == 'POST':
        print('okay')
        gradeemail = request.form['email']
        justemail = gradeemail.split('@')
        gradecourse = request.form['course']
        gradesection = request.form['sec']
        grade = request.form['grade']
        exam = request.form['exam']
        getnumexam = exam.split()
        tempexam = int(getnumexam[1])
        connection.execute(
            'UPDATE Homeworks_grade '
            'SET grade = ? '
            'WHERE semail = ? AND cid = ? AND sec_no = ? AND hw_no = ?;',
            (grade, justemail[0], gradecourse, gradesection, tempexam))
        connection.commit()
        return redirect('/homeworkGradeP')
    if sethw:
        return render_template('homeworkGradeP.html', error=error, gradehw=sethw)
    else:
        error = 'invalid input name'
    return render_template('homeworkGradeP.html', error=error)


@app.route('/newhomework', methods=['POST', 'GET'])
def newhomework():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT Sec.cid '
                                'FROM Students S, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail',
                                (myid, mypw))
    teach = cursor.fetchall()
    courses = []
    for set in teach:
        courses.append(set[0])
    cursor = connection.execute('SELECT DISTINCT Sec.sec_no '
                                'FROM Students S, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail',
                                (myid, mypw))
    teachsec = cursor.fetchall()
    sections = []
    for set in teachsec:
        sections.append(set[0])
    if request.method == 'POST':
        tempcourse = request.form['cid']
        tempsection = int(request.form['sec'])
        temptitle = int(request.form['title'])
        tempnote = request.form['note']
        connection.execute(
            'INSERT INTO Homeworks (cid, sec_no, hw_no, hwdesc) VALUES (?,?,?,?)', (tempcourse, tempsection, temptitle, tempnote))
        connection.commit()
        cursor = connection.execute('SELECT S.semail '
                                    'FROM Students S, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                    'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                    'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail AND Sec.sec_no = ? AND Sec.cid = ?',
                                    (myid, mypw, tempsection, tempcourse))
        getsemail = cursor.fetchall()
        cursor = connection.execute(
            'SELECT TA.semail '
            'FROM TA, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
            'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
            'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND TA.semail = E.semail AND Sec.sec_no = ? AND Sec.cid = ?',
            (myid, mypw, tempsection, tempcourse))
        gettaemail = cursor.fetchall()
        tempnumber = ' '
        for set in getsemail:
            connection.execute(
                'INSERT INTO Homeworks_grade (semail, cid, sec_no, hw_no, grade) VALUES (?,?,?,?,?)',
                (set[0], tempcourse, tempsection, temptitle, tempnumber))
            connection.commit()
        for set in gettaemail:
            connection.execute(
                'INSERT INTO Homeworks_grade (semail, cid, sec_no, hw_no, grade) VALUES (?,?,?,?,?)',
                (set[0], tempcourse, tempsection, temptitle, tempnumber))
            connection.commit()
        return redirect('/homeworkP')
    if courses:
        return render_template('homeworknewP.html', error=error, courses=courses, sections=sections)
    else:
        error = 'invalid input name'
    return render_template('homeworknewP.html', error=error)


@app.route('/deletehomeworkP', methods=['POST', 'GET'])
def deletehomeworkP():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT H.cid, H.sec_no, H.hw_no, H.hwdesc '
                                'FROM Professors P, Professor_teach PT, Sections Sec, Homeworks H '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.sec_no = H.sec_no AND Sec.cid = H.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;', (myid, mypw))
    hwdue = cursor.fetchall()
    sethw = []
    for set in hwdue:
        tempname = 'Homework ' + str(set[2])
        sethw.append([set[0], set[1], tempname, set[3]])
    if request.method == 'POST':
        getcourse = request.form['class']
        getsection = request.form['sec']
        gethomework = request.form['homework']
        gethwdesc = request.form['hwdesc']
        thehw = gethomework.split(' ')
        hwnum = int(thehw[1])
        connection.execute(
            'DELETE FROM Homeworks WHERE cid = ? AND sec_no = ? AND hw_no = ? AND hwdesc = ? ;', (getcourse, getsection, hwnum, gethwdesc))
        connection.commit()
        connection.execute(
            'DELETE FROM Homeworks_grade WHERE cid = ? AND sec_no = ? AND hw_no = ?;',
            (getcourse, getsection, hwnum))
        connection.commit()
        return redirect('/homeworkP')
    if sethw:
        return render_template('deletehomework.html', error=error, hwdue=sethw)
    else:
        error = 'invalid input name'
    return render_template('deletehomework.html', error=error)


@app.route('/deleteexamP', methods=['POST', 'GET'])
def deleteExamP():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT Ex.cid, Ex.sec_no, Ex.exam_no, Ex.examdesc '
                                'FROM Professors P, Professor_teach PT, Sections Sec, Exams Ex '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.sec_no = Ex.sec_no AND Sec.cid = Ex.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;', (myid, mypw))
    examdue = cursor.fetchall()
    setexam = []
    for set in examdue:
        tempname = 'Exam ' + str(set[2])
        setexam.append([set[0], set[1], tempname, set[3]])
    if request.method == 'POST':
        getcourse = request.form['class']
        getsection = request.form['sec']
        getexam = request.form['exam']
        getexamdesc = request.form['examdesc']
        theexam = getexam.split(' ')
        examnum = int(theexam[1])
        connection.execute(
            'DELETE FROM Exams WHERE cid = ? AND sec_no = ? AND exam_no = ? AND examdesc = ? ;', (getcourse, getsection, examnum, getexamdesc))
        connection.commit()
        connection.execute(
            'DELETE FROM Exams_grade WHERE cid = ? AND sec_no = ? AND exam_no = ?;',
            (getcourse, getsection, examnum))
        connection.commit()
        return redirect('/examP')
    if setexam:
        return render_template('deleteexam.html', error=error, hwdue=setexam)
    else:
        error = 'invalid input name'
    return render_template('deleteexam.html', error=error)


@app.route('/examGradeP', methods=['POST', 'GET'])
def examGradeP():
    error = None
    connection = sql.connect('database.db')
    examno = tempexam.split()
    cursor = connection.execute('SELECT S.firstname, S.lastname, S.semail, Sec.cid, Sec.sec_no, Ex.exam_no, Eg.grade '
                                'FROM Professors P, Professor_teach Pt, Sections Sec, Enrolls E, Exams Ex, Students S, Exams_grade Eg '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail AND E.cid = Ex.cid AND Ex.sec_no = E.sec_no AND '
                                '? = Sec.sec_no AND Eg.cid = Ex.cid AND Eg.sec_no = Ex.sec_no AND Eg.exam_no = Ex.exam_no AND Eg.semail = E.semail AND Eg.exam_no = ?;',
                                (myid, mypw, tempsection, int(examno[1])))
    studenthw = cursor.fetchall()
    cursor = connection.execute('SELECT TA.firstname, TA.lastname, TA.semail, Sec.cid, Sec.sec_no, Ex.exam_no, Eg.grade '
                                'FROM Professors P, Professor_teach Pt, Sections Sec, Enrolls E, Exams Ex, TA, Exams_grade Eg '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND TA.semail = E.semail AND E.cid = Ex.cid AND Ex.sec_no = E.sec_no AND '
                                '? = Sec.sec_no AND Eg.cid = Ex.cid AND Eg.sec_no = Ex.sec_no AND Eg.exam_no = Ex.exam_no AND Eg.semail = E.semail AND Eg.exam_no = ?;', (myid, mypw, tempsection, int(examno[1])))
    TAhw = cursor.fetchall()
    sethw = []  # append
    for set in studenthw:
        tempstudents = set[0] + ' ' + set[1]
        tempemail = set[2] + '@Nittanystate.edu'
        tempname = 'Exam ' + str(set[5])
        sethw.append([tempstudents, tempemail, set[3],
                      set[4], tempname, set[6]])
    for set in TAhw:
        tempstudents = set[0] + ' ' + set[1]
        tempemail = set[2] + '@Nittanystate.edu'
        tempname = 'Exam ' + str(set[5])
        sethw.append([tempstudents, tempemail, set[3],
                      set[4], tempname, set[6]])
    if request.method == 'POST':
        gradeemail = request.form['email']
        justemail = gradeemail.split('@')
        gradecourse = request.form['course']
        gradesection = request.form['sec']
        grade = request.form['grade']
        exam = request.form['exam']
        getnumexam = exam.split()
        tempexam1 = int(getnumexam[1])
        connection.execute(
            'UPDATE Exams_grade '
            'SET grade = ? '
            'WHERE semail = ? AND cid = ? AND sec_no = ? AND exam_no = ?;',
            (grade, justemail[0], gradecourse, gradesection, tempexam1))
        connection.commit()
        return redirect('/examGradeP')
    if sethw:
        return render_template('examGradeP.html', error=error, examhw=sethw)
    else:
        error = 'invalid input name'
    return render_template('examGradeP.html', error=error)


@app.route('/examP', methods=['POST', 'GET'])
def examP():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT Ex.cid, Ex.sec_no, Ex.exam_no, Ex.examdesc '
                                'FROM Professors P, Professor_teach PT, Sections Sec, Exams Ex '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.sec_no = Ex.sec_no AND Sec.cid = Ex.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;', (myid, mypw))
    examdue = cursor.fetchall()
    setexam = []
    for set in examdue:
        tempname = 'Exam ' + str(set[2])
        setexam.append([set[0], set[1], tempname, set[3]])
    if request.method == 'POST':
        global tempcourse
        tempcourse = request.form['class']
        global tempsection
        tempsection = request.form['sec']
        global tempexam
        tempexam = request.form['exam']
        global tempexamdesc
        tempexamdesc = request.form['examdesc']
        return redirect('/examGradeP')
    if setexam:
        return render_template('examP.html', error=error, examdue=setexam)
    else:
        error = 'invalid input name'
    return render_template('examP.html', error=error)


@app.route('/newexam', methods=['POST', 'GET'])
def newexam():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT Sec.cid '
                                'FROM Students S, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail',
                                (myid, mypw))
    teach = cursor.fetchall()
    courses = []
    for set in teach:
        courses.append(set[0])
    cursor = connection.execute('SELECT DISTINCT Sec.sec_no '
                                'FROM Students S, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail',
                                (myid, mypw))
    teachsec = cursor.fetchall()
    sections = []
    for set in teachsec:
        sections.append(set[0])

    if request.method == 'POST':
        tempcourse = request.form['cid']
        tempsection = int(request.form['sec'])
        temptitle = int(request.form['title'])
        tempnote = request.form['note']
        connection.execute(
            'INSERT INTO Exams (cid, sec_no, exam_no, examdesc) VALUES (?,?,?,?)', (tempcourse, tempsection, temptitle, tempnote))
        connection.commit()
        cursor = connection.execute('SELECT S.semail '
                                    'FROM Students S, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
                                    'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
                                    'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail AND Sec.sec_no = ? AND Sec.cid = ?',
                                    (myid, mypw, tempsection, tempcourse))
        getsemail = cursor.fetchall()
        cursor = connection.execute(
            'SELECT TA.semail '
            'FROM TA, Enrolls E, Sections Sec, Professor_teach PT, Professors P '
            'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND Sec.teaching_team_id = PT.teaching_team_id '
            'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND TA.semail = E.semail AND Sec.sec_no = ? AND Sec.cid = ?',
            (myid, mypw, tempsection, tempcourse))
        gettaemail = cursor.fetchall()
        tempnumber = ' '
        for set in getsemail:
            connection.execute(
                'INSERT INTO Exams_grade (semail, cid, sec_no, exam_no, grade) VALUES (?,?,?,?,?)',
                (set[0], tempcourse, tempsection, temptitle, tempnumber))
            connection.commit()
        for set in gettaemail:
            connection.execute(
                'INSERT INTO Exams_grade (semail, cid, sec_no, exam_no, grade) VALUES (?,?,?,?,?)',
                (set[0], tempcourse, tempsection, temptitle, tempnumber))
            connection.commit()
        return redirect('/examP')

    if courses:
        return render_template('examnewP.html', error=error, courses=courses, sections=sections)
    else:
        error = 'invalid input name'
    return render_template('examnewP.html', error=error)


@app.route('/inboxp', methods=['POST', 'GET'])
def inboxp():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, S2.firstname, S2.lastname, M.adate, M.atime, S2.semail '
        'FROM Professors P, Message M, Students S2 '
        'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = M.receiveby AND M.sendby = S2.semail',
        (myid, mypw))
    messageS = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, TA.firstname, TA.lastname, M.adate, M.atime, TA.semail '
        'FROM Professors P, Message M, TA '
        'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = M.receiveby AND M.sendby = TA.semail',
        (myid, mypw))
    messageTA = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, P2.firstname, P2.lastname, M.adate, M.atime, P2.pemail '
        'FROM Professors P, Message M, Professors P2 '
        'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = M.receiveby AND M.sendby = P2.pemail',
        (myid, mypw))
    messageP = cursor1.fetchall()
    tempmess = []
    for set in messageS:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageTA:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageP:
        tempname = 'Dr. ' + set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    if request.method == 'POST':
        global temptitle
        temptitle = request.form['title']
        global tempdate
        tempdate = request.form['date']
        global temptime
        temptime = request.form['time']
        global tempemail
        tempemail = request.form['email']
        global tempflname
        tempflname = request.form['sent']
        return redirect('/readinboxp')
    if tempmess:
        return render_template('messageinboxp.html', error=error, myinbox=tempmess)
    else:
        error = 'invalid input name'
    return render_template('messageinboxp.html', error=error)


@app.route('/sentp', methods=['POST', 'GET'])
def sentp():
    error = ' '
    connection = sql.connect('database.db')
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, S2.firstname, S2.lastname, M.adate, M.atime, S2.semail '
        'FROM Professors P, Message M, Students S2 '
        'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = M.sendby AND M.receiveby = S2.semail',
        (myid, mypw))
    messageS = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, TA.firstname, TA.lastname, M.adate, M.atime, TA.semail '
        'FROM Professors P, Message M, TA '
        'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = M.sendby AND M.receiveby = TA.semail',
        (myid, mypw))
    messageTA = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT M.title, P2.firstname, P2.lastname, M.adate, M.atime, P2.pemail '
        'FROM Professors P, Message M, Professors P2 '
        'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = M.sendby AND M.receiveby = P2.pemail',
        (myid, mypw))
    messageP = cursor1.fetchall()

    tempmess = []
    for set in messageS:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageTA:
        tempname = set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    for set in messageP:
        tempname = 'Dr. ' + set[1] + ' ' + set[2]
        tempmess.append([set[0], tempname, set[3], set[4], set[5]])
    if request.method == 'POST':
        global temptitle
        temptitle = request.form['title']
        global tempdate
        tempdate = request.form['date']
        global temptime
        temptime = request.form['time']
        global tempemail
        tempemail = request.form['email']
        global tempflname
        tempflname = request.form['sent']
        return redirect('/readsentp')
    if tempmess:
        return render_template('messagesentp.html', error=error, mysent=tempmess)
    else:
        error = 'invalid input name'
    return render_template('messagesentp.html', error=error)


@app.route('/compostp', methods=['POST', 'GET'])
def compostp():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT S.semail FROM Students S')
    getStudents = cursor.fetchall()
    cursor = connection.execute('SELECT TA.semail FROM TA')
    getTAs = cursor.fetchall()
    cursor = connection.execute('SELECT P.pemail FROM Professors P')
    getProfessors = cursor.fetchall()
    allMember = []
    for set in getStudents:
        allMember.append(set[0])
    for set in getTAs:
        allMember.append(set[0])
    for set in getProfessors:
        allMember.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getReceiver = request.form['messageto']
        if getReceiver in allMember:
            receiver = getReceiver
            getTitle = request.form['messagetitle']
            getNote = request.form['messagenote']
            connection.execute(
                'INSERT INTO Message(sendby, receiveby, adate, atime, title, note) VALUES (?,?,?,?,?,?);',
                (myid, receiver, getdate, gettime, getTitle, getNote))
            connection.commit()
            return redirect('/inboxp')
        else:
            error = "The person you send to is invalid. Please try again."
    return render_template('messagecompostp.html', error=error)


@app.route('/readinboxp', methods=['POST', 'GET'])
def readinboxp():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM Professors P, Message M, Students S2 '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = M.receiveby AND S2.semail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessage = cursor.fetchall()
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM Professors P, Message M, TA '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = M.receiveby AND TA.semail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessaget = cursor.fetchall()
    cursor = connection.execute('SELECT Distinct M.sendby, M.adate, M.atime, M.title, M.note '
                                'FROM Professors P, Message M, Professors P2 '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = M.receiveby AND P2.pemail = M.sendby AND ? = M.title AND ? = M.adate AND ? = M.atime AND ? = M.sendby',
                                (myid, mypw, temptitle, tempdate, temptime, tempemail))
    getmessagep = cursor.fetchall()
    message = []
    for set in getmessage:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    for set in getmessaget:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    for set in getmessagep:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    if message:
        return render_template('messagereadp.html', error=error, message=message)
    else:
        error = "The person you send to is invalid. Please try again."
    return render_template('messagereadp.html', error=error)


@app.route('/readsentp', methods=['POST', 'GET'])
def readsentp():
    error = ' '
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT Distinct M.receiveby, M.adate, M.atime, M.title, M.note '
                                'FROM Professors P, Message M '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = M.sendby AND ? = M.receiveby AND ? = M.adate AND ? = M.atime AND ? = M.title',
                                (myid, mypw, tempemail, tempdate, temptime, temptitle))
    getmessage = cursor.fetchall()
    message = []
    for set in getmessage:
        message.append([set[0], set[1], set[2], set[3], set[4], tempflname])
    if message:
        return render_template('messageread2p.html', error=error, message=message)
    else:
        error = "The person you send to is invalid. Please try again."
    return render_template('messageread2p.html', error=error)


@app.route('/appointmentP', methods=['POST', 'GET'])
def appointmentP():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT A.semail, A.title, A.adate, A.atime, A.note '
                                 'FROM Professors P, Appointment A '
                                 'WHERE ? = P.pemail AND ? = P.password AND P.pemail = A.witheamil',
                                 (myid, mypw))
    myappointment = cursor1.fetchall()

    myappo = []
    for set in myappointment:
        myappo.append([set[0], set[1], set[4], set[2], set[3]])

    if request.method == 'POST':
        getemail = request.form['email']
        getdate = request.form['date']
        gettime = request.form['time']
        connection.execute(
            'DELETE FROM Appointment WHERE witheamil = ? AND semail = ? AND adate = ? AND atime = ?;', (myid, getemail, getdate, gettime))
        connection.commit()
        return redirect('/appointmentP')
    if myappointment:
        return render_template('appointmentP.html', error=error, myappo=myappo)
    else:
        error = 'invalid input name'
    return render_template('appointmentP.html', error=error)


@app.route('/forumP', methods=['POST', 'GET'])
def forumP():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S.firstname, S.lastname, Pt.post_no '
                                'FROM Students S, Professor_teach PT, Posts Pt, Professors P, Sections Sec '
                                'WHERE ? = P.pemail AND P.pemail = PT.pemail AND PT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND Pt.semail = S.semail;',
                                (myid,))
    forumS = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, TA.firstname, TA.lastname, Pt.post_no '
                                'FROM TA, Professor_teach PT, Posts Pt, Professors P, Sections Sec '
                                'WHERE ? = P.pemail AND P.pemail = PT.pemail AND PT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND Pt.semail = TA.semail;',
                                (myid,))
    forumT = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, P2.firstname, P2.lastname, Pt.post_no '
                                'FROM Professors P2, Professor_teach PT, Posts Pt, Professors P, Sections Sec '
                                'WHERE ? = P.pemail AND P.pemail = PT.pemail AND PT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND Pt.semail = P2.pemail;',
                                (myid,))
    forumP = cursor.fetchall()
    tempforum = []
    for set in forumS:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forumT:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forumP:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    if request.method == 'POST':
        global temppostnum
        temppostnum = request.form['postnum']
        return redirect('/commentP')
    if tempforum:
        return render_template('forumP.html', error=error, forum=tempforum)
    else:
        error = 'invalid input name'
    return render_template('forumP.html', error=error)


@app.route('/deleteforum', methods=['POST', 'GET'])
def deleteforum():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S.firstname, S.lastname, Pt.post_no '
                                'FROM Students S, Professor_teach PT, Posts Pt, Professors P, Sections Sec '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND PT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND Pt.semail = S.semail;',
                                (myid, mypw))
    forumS = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, TA.firstname, TA.lastname, Pt.post_no '
                                'FROM TA, Professor_teach PT, Posts Pt, Professors P, Sections Sec '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND PT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND Pt.semail = TA.semail;',
                                (myid, mypw))
    forumT = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, P2.firstname, P2.lastname, Pt.post_no '
                                'FROM Professors P2, Professor_teach PT, Posts Pt, Professors P, Sections Sec '
                                'WHERE ? = P.pemail AND ? = P.password AND P.pemail = PT.pemail AND PT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND Pt.semail = P2.pemail;',
                                (myid, mypw))
    forumP = cursor.fetchall()
    tempforum = []
    for set in forumS:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forumT:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forumP:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    if request.method == 'POST':
        global temppostnum
        temppostnum = request.form['postnum']
        connection.execute(
            'DELETE FROM Posts WHERE post_no = ?;', (temppostnum,))
        connection.commit()
        return redirect('/forumP')
    if forum:
        return render_template('deleteforum.html', error=error, forum=tempforum)
    else:
        error = 'invalid input name'
    return render_template('deleteforum.html', error=error)


@app.route('/createforumP', methods=['POST', 'GET'])
def createforumP():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT Sec.cid  '
                                 'FROM Professors P, Professor_teach Pt, Sections Sec '
                                 'WHERE ? = P.pemail AND ? = P.Password AND P.pemail = Pt.pemail AND Pt.teaching_team_id = Sec.teaching_team_id',
                                 (myid, mypw))
    myclass = cursor1.fetchall()
    courses = []
    for set in myclass:
        courses.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getcid = request.form['cid']
        gettitle = request.form['title']
        getnote = request.form['note']
        connection.execute(
            'INSERT INTO Posts (semail, cid, pdate, ptime, ptitle, postdesc) VALUES (?,?,?,?,?,?)', (myid, getcid, getdate, gettime, gettitle, getnote))
        connection.commit()
        return redirect('/forumP')
    if myclass:
        return render_template('createforumP.html', error=error, myclass=courses)
    else:
        error = 'invalid input name'
    return render_template('createforumP.html', error=error)


@app.route('/commentP', methods=['POST', 'GET'])
def commentP():
    error = None
    connection = sql.connect('database.db')
    print(temppostnum)
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, Professors S, Students S2 '
        'WHERE ? = S.pemail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.semail',
        (myid, mypw, temppostnum))
    forum = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, Professors S, TA S2 '
        'WHERE ? = S.pemail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.semail',
        (myid, mypw, temppostnum))
    forum1 = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, Professors S, Professors S2 '
        'WHERE ? = S.pemail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.pemail',
        (myid, mypw, temppostnum))
    forum2 = cursor1.fetchall()
    tempforum = []
    for set in forum:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum1:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum2:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    print(tempforum)
    cursor1 = connection.execute(
        'SELECT DISTINCT Com.pdate, Com.ptime, Students.firstname, Students.lastname, Com.comdesc, Com.post_no '
        'FROM Students, Comments Com '
        'WHERE ? = Com.post_no AND Com.semail = Students.semail;',
        (temppostnum,))
    comment = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Com.pdate, Com.ptime, TA.firstname, TA.lastname, Com.comdesc, Com.post_no '
        'FROM TA, Comments Com '
        'WHERE ? = Com.post_no AND Com.semail = TA.semail;',
        (temppostnum,))
    commentTA = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Com.pdate, Com.ptime, P.firstname, P.lastname, Com.comdesc, Com.post_no '
        'FROM Professors P, Comments Com '
        'WHERE ? = Com.post_no AND Com.semail = P.pemail;',
        (temppostnum,))
    commentP = cursor1.fetchall()
    tempcomment = []
    for set in comment:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    for set in commentTA:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    for set in commentP:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    print(cidnum)
    print(temppostnum)
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")
        getnote = request.form['com']
        connection.execute(
            'INSERT INTO Comments (cid, post_no, pdate, ptime, semail, comdesc) VALUES (?,?,?,?,?,?)',
            (cidnum, temppostnum, getdate, gettime, myid, getnote))
        connection.commit()
        return redirect('/commentP')
    if tempforum:
        return render_template('commentP.html', error=error, forum=tempforum, comment=tempcomment)
    else:
        error = 'invalid input name'
    return render_template('commentP.html', error=error)


@app.route('/TATA', methods=['POST', 'GET'])
def TATA():
    error = None
    connection = sql.connect('database.db')
    # my info
    cursor = connection.execute(
        'SELECT S.firstname, S.lastname, S.semail, S.age, S.gender, S.major FROM TA S WHERE ? = S.semail AND ? = S.password;',
        (myid, mypw))
    myinfo = cursor.fetchall()
    mygender = None
    if myinfo[0][4] == 'F':
        mygender = 'Female'
    elif myinfo[0][4] == 'M':
        mygender = 'Male'
    changemyinfo = [myinfo[0][0] + ' ' + myinfo[0][1],
                    myinfo[0][2], myinfo[0][3], mygender, myinfo[0][5]]
    setinfo = [(None, None, None, None, None)]
    setinfo[0] = changemyinfo
    # my Students
    cursor = connection.execute('SELECT Sec.cid, S.firstname, S.lastname, Sec.sec_no, S.age, S.gender, S.major '
                                'FROM Students S, Enrolls E, Sections Sec, TA_teach PT, TA P '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail ORDER BY S.lastname ASC LIMIT 5',
                                (myid, mypw))
    mystudents = cursor.fetchall()
    setstudent = []  # append
    for set in mystudents:
        gen = None
        if set[5] == 'F':
            gen = 'Female'
        elif set[5] == 'M':
            gen = 'Male'
        tempstudents = set[1] + ' ' + set[2]
        setstudent.append([set[0], tempstudents, set[3], set[4], gen, set[6]])
    # my coming up
    cursor = connection.execute('SELECT DISTINCT H.cid, H.hw_no, H.hwdesc '
                                'FROM TA P, TA_Teach PT, Sections Sec, Homeworks H '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.sec_no = H.sec_no AND Sec.cid = H.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;',
                                (myid, mypw))
    hwdue = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT Ex.cid, Ex.exam_no, Ex.examdesc '
                                'FROM TA P, TA_Teach PT, Sections Sec, Exams Ex '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.sec_no = Ex.sec_no AND Sec.cid = Ex.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;',
                                (myid, mypw))
    exam = cursor.fetchall()
    mydue = []
    for set in hwdue:
        tempname = 'Homework ' + str(set[1])
        tempset = [set[0], tempname, set[2]]
        mydue.append(tempset)
    for set in exam:
        tempname = 'Exam ' + str(set[1])
        tempset = [set[0], tempname, set[2]]
        mydue.append(tempset)
    if setinfo:
        return render_template('main_Teach_TA.html', error=error, myinfo=setinfo, mystudent=setstudent,
                               mydue=mydue)
    else:
        error = 'invalid input name'
    return render_template('main_Teach_TA.html', error=error)


@app.route('/studentsTATA', methods=['POST', 'GET'])
def mystudentsTATA():
    error = None
    connection = sql.connect('database.db')
    allstud = []
    cursor = connection.execute('SELECT Sec.cid, S.firstname, S.lastname, Sec.sec_no, S.age, S.gender, S.major '
                                'FROM Students S, Enrolls E, Sections Sec, TA_teach PT, TA P '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail ORDER BY S.lastname',
                                (myid, mypw))
    mystudents = cursor.fetchall()
    cursor = connection.execute('SELECT Sec.cid, S.firstname, S.lastname, Sec.sec_no, S.age, S.gender, S.major '
                                'FROM TA S, Enrolls E, Sections Sec, TA_teach PT, TA P '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail ORDER BY S.lastname',
                                (myid, mypw))
    mystudentt = cursor.fetchall()
    for set in mystudents:
        gen = None
        if set[5] == 'F':
            gen = 'Female'
        elif set[5] == 'M':
            gen = 'Male'
        tempstudents = set[1] + ' ' + set[2]
        allstud.append([set[0], tempstudents, set[3], set[4], gen, set[6]])
    for set in mystudentt:
        gen = None
        if set[5] == 'F':
            gen = 'Female'
        elif set[5] == 'M':
            gen = 'Male'
        tempstudents = set[1] + ' ' + set[2]
        allstud.append([set[0], tempstudents, set[3], set[4], gen, set[6]])
    if allstud:
        return render_template('studentsTATA.html', error=error, allstud=allstud)
    else:
        error = 'invalid input name'
    return render_template('studentsTATA.html', error=error)


@app.route('/homeworkTATA', methods=['POST', 'GET'])
def homeworkTATA():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT H.cid, H.sec_no, H.hw_no, H.hwdesc '
                                'FROM TA P, TA_teach PT, Sections Sec, Homeworks H '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.sec_no = H.sec_no AND Sec.cid = H.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;', (myid, mypw))
    hwdue = cursor.fetchall()
    sethw = []
    for set in hwdue:
        tempname = 'Homework ' + str(set[2])
        sethw.append([set[0], set[1], tempname, set[3]])
    if request.method == 'POST':
        global tempcourse
        tempcourse = request.form['class']
        global tempsection
        tempsection = request.form['sec']
        global temphomework
        temphomework = request.form['homework']
        global temphwdesc
        temphwdesc = request.form['hwdesc']
        return redirect('/homeworkGradeTATA')
    if sethw:
        return render_template('homeworkTATA.html', error=error, hwdue=sethw)
    else:
        error = 'invalid input name'
    return render_template('homeworkTATA.html', error=error)


@app.route('/homeworkGradeTATA', methods=['POST', 'GET'])
def homeworkGradeTATA():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT S.firstname, S.lastname, S.semail, Sec.cid, Sec.sec_no, H.hw_no, Hg.grade '
                                'FROM TA P, TA_teach Pt, Sections Sec, Enrolls E, Homeworks H, Students S, Homeworks_grade Hg '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail AND H.cid = E.cid AND H.sec_no = E.sec_no AND '
                                'Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND Hg.hw_no = H.hw_no AND Hg.semail = E.semail AND '
                                '? = Sec.cid AND ? = Sec.sec_no AND ? = H.hwdesc;',
                                (myid, mypw, tempcourse, tempsection, temphwdesc))
    studenthw = cursor.fetchall()
    cursor = connection.execute('SELECT TA.firstname, TA.lastname, TA.semail, Sec.cid, Sec.sec_no, H.hw_no, Hg.grade '
                                'FROM TA P, TA_teach Pt, Sections Sec, Enrolls E, Homeworks H, TA, Homeworks_grade Hg '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND TA.semail = E.semail AND H.cid = E.cid AND H.sec_no = E.sec_no AND '
                                'Hg.cid = H.cid AND Hg.sec_no = H.sec_no AND Hg.hw_no = H.hw_no AND Hg.semail = E.semail AND '
                                '? = Sec.cid AND ? = Sec.sec_no AND ? = H.hwdesc;', (myid, mypw, tempcourse, tempsection, temphwdesc))
    TAhw = cursor.fetchall()
    sethw = []  # append
    for set in studenthw:
        tempstudents = set[0] + ' ' + set[1]
        tempemail = set[2] + '@Nittanystate.edu'
        tempname = 'Homework ' + str(set[5])
        sethw.append([tempstudents, tempemail, set[3],
                      set[4], tempname, set[6]])
    for set in TAhw:
        tempstudents = set[0] + ' ' + set[1]
        tempemail = set[2] + '@Nittanystate.edu'
        tempname = 'Homework ' + str(set[5])
        sethw.append([tempstudents, tempemail, set[3],
                      set[4], tempname, set[6]])
    if request.method == 'POST':
        print('okay')
        gradeemail = request.form['email']
        justemail = gradeemail.split('@')
        gradecourse = request.form['course']
        gradesection = request.form['sec']
        grade = request.form['grade']
        exam = request.form['exam']
        getnumexam = exam.split()
        tempexam = int(getnumexam[1])
        connection.execute(
            'UPDATE Homeworks_grade '
            'SET grade = ? '
            'WHERE semail = ? AND cid = ? AND sec_no = ? AND hw_no = ?;',
            (grade, justemail[0], gradecourse, gradesection, tempexam))
        connection.commit()
        return redirect('/homeworkGradeTATA')
    if sethw:
        return render_template('homeworkGradeTATA.html', error=error, gradehw=sethw)
    else:
        error = 'invalid input name'
    return render_template('homeworkGradeTATA.html', error=error)


@app.route('/examGradeTATA', methods=['POST', 'GET'])
def examGradeTATA():
    error = None
    connection = sql.connect('database.db')
    examno = tempexam.split()
    cursor = connection.execute('SELECT S.firstname, S.lastname, S.semail, Sec.cid, Sec.sec_no, Ex.exam_no, Eg.grade '
                                'FROM TA P, TA_teach Pt, Sections Sec, Enrolls E, Exams Ex, Students S, Exams_grade Eg '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND S.semail = E.semail AND E.cid = Ex.cid AND Ex.sec_no = E.sec_no AND '
                                '? = Sec.sec_no AND Eg.cid = Ex.cid AND Eg.sec_no = Ex.sec_no AND Eg.exam_no = Ex.exam_no AND Eg.semail = E.semail AND Eg.exam_no = ?;',
                                (myid, mypw, tempsection, int(examno[1])))
    studenthw = cursor.fetchall()
    cursor = connection.execute('SELECT TA.firstname, TA.lastname, TA.semail, Sec.cid, Sec.sec_no, Ex.exam_no, Eg.grade '
                                'FROM TA P, TA_teach Pt, Sections Sec, Enrolls E, Exams Ex, TA, Exams_grade Eg '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.teaching_team_id = PT.teaching_team_id '
                                'AND E.sec_no = Sec.sec_no AND Sec.cid = E.cid AND TA.semail = E.semail AND E.cid = Ex.cid AND Ex.sec_no = E.sec_no AND '
                                '? = Sec.sec_no AND Eg.cid = Ex.cid AND Eg.sec_no = Ex.sec_no AND Eg.exam_no = Ex.exam_no AND Eg.semail = E.semail AND Eg.exam_no = ?;', (myid, mypw, tempsection, int(examno[1])))
    TAhw = cursor.fetchall()
    sethw = []  # append
    for set in studenthw:
        tempstudents = set[0] + ' ' + set[1]
        tempemail = set[2] + '@Nittanystate.edu'
        tempname = 'Exam ' + str(set[5])
        sethw.append([tempstudents, tempemail, set[3],
                      set[4], tempname, set[6]])
    for set in TAhw:
        tempstudents = set[0] + ' ' + set[1]
        tempemail = set[2] + '@Nittanystate.edu'
        tempname = 'Exam ' + str(set[5])
        sethw.append([tempstudents, tempemail, set[3],
                      set[4], tempname, set[6]])
    if request.method == 'POST':
        gradeemail = request.form['email']
        justemail = gradeemail.split('@')
        gradecourse = request.form['course']
        gradesection = request.form['sec']
        grade = request.form['grade']
        exam = request.form['exam']
        getnumexam = exam.split()
        tempexam1 = int(getnumexam[1])
        connection.execute(
            'UPDATE Exams_grade '
            'SET grade = ? '
            'WHERE semail = ? AND cid = ? AND sec_no = ? AND exams_no = ?;',
            (grade, justemail[0], gradecourse, gradesection, tempexam1))
        connection.commit()
        return redirect('/examGradeTATA')
    if sethw:
        return render_template('examGradeTATA.html', error=error, examhw=sethw)
    else:
        error = 'invalid input name'
    return render_template('examGradeTATA.html', error=error)


@app.route('/examTATA', methods=['POST', 'GET'])
def examTATA():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT Ex.cid, Ex.sec_no, Ex.exam_no, Ex.examdesc '
                                'FROM TA P, TA_teach PT, Sections Sec, Exams Ex '
                                'WHERE ? = P.semail AND ? = P.password AND P.semail = PT.semail AND Sec.sec_no = Ex.sec_no AND Sec.cid = Ex.cid '
                                'AND PT.teaching_team_id = Sec.teaching_team_id;', (myid, mypw))
    examdue = cursor.fetchall()
    setexam = []
    for set in examdue:
        tempname = 'Exam ' + str(set[2])
        setexam.append([set[0], set[1], tempname, set[3]])
    if request.method == 'POST':
        global tempcourse
        tempcourse = request.form['class']
        global tempsection
        tempsection = request.form['sec']
        global tempexam
        tempexam = request.form['exam']
        global tempexamdesc
        tempexamdesc = request.form['examdesc']
        return redirect('/examGradeTATA')
    if setexam:
        return render_template('examTATA.html', error=error, examdue=setexam)
    else:
        error = 'invalid input name'
    return render_template('examTATA.html', error=error)


@app.route('/announcementsTATA', methods=['POST', 'GET'])
def announcementsTATA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.anno_no, A.cid, A.ptitle, P.firstname, P.lastname '
                                 'FROM Announcements A , TA_teach Pt, TA P, Sections Sec '
                                 'WHERE ? = P.semail AND ? = P.Password AND P.semail = Pt.semail AND Pt.teaching_team_id = Sec.teaching_team_id AND Sec.cid = A.cid '
                                 'ORDER BY A.anno_no DESC',
                                 (myid, mypw))
    announcements = cursor1.fetchall()
    setannouncements = []
    for set in announcements:
        tempname = set[3] + ' ' + set[4]
        setannouncements.append([set[0], set[1], set[2], tempname])
    if request.method == 'POST':
        global tempanum
        tempanum = request.form['postnum']
        global cidanum
        cidanum = request.form['class']
        return redirect('/viewannouncementsTATA')
    if setannouncements:
        return render_template('announcementsTATA.html', error=error, forum=setannouncements)
    else:
        error = 'invalid input name'
    return render_template('announcementsTATA.html', error=error)


@app.route('/createannouncementsTATA', methods=['POST', 'GET'])
def createannouncementsTATA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT Sec.cid  '
                                 'FROM TA P, TA_teach Pt, Sections Sec '
                                 'WHERE ? = P.semail AND ? = P.Password AND P.semail = Pt.semail AND Pt.teaching_team_id = Sec.teaching_team_id ',
                                 (myid, mypw))
    myclass = cursor1.fetchall()
    courses = []
    for set in myclass:
        courses.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getcid = request.form['cid']
        gettitle = request.form['title']
        getnote = request.form['note']
        connection.execute(
            'INSERT INTO Announcements (cid, pdate, ptime, ptitle, pemail, postdesc) VALUES (?,?,?,?,?,?)', (getcid, getdate, gettime, gettitle, myid, getnote))
        connection.commit()
        return redirect('/announcementsTATA')
    if courses:
        return render_template('createannouncementsTATA.html', error=error, myclass=courses)
    else:
        error = 'invalid input name'
    return render_template('createannouncementsTATA.html', error=error)


@app.route('/viewannouncementsTATA', methods=['POST', 'GET'])
def viewannouncementsTATA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT A.cid, A.ptitle, P.firstname, P.lastname, A.postdesc, A.pdate, A.ptime '
                                 'FROM Announcements A, TA P '
                                 'WHERE ? = P.semail AND ? = P.Password AND ? = A.anno_no AND ? = A.cid ',
                                 (myid, mypw, tempanum, cidanum))
    forum = cursor1.fetchall()
    tempforum = []
    for set in forum:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    return render_template('viewannouncementsTATA.html', error=error, forum=tempforum)


@app.route('/forumTATA', methods=['POST', 'GET'])
def forumTATA():
    error = None
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, S.firstname, S.lastname, Pt.post_no '
                                'FROM Students S, TA_teach TT, Posts Pt, TA P, Sections Sec '
                                'WHERE ? = P.semail AND TT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND P.semail = TT.semail AND Pt.semail = S.semail;',
                                (myid,))
    forumS = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, TA.firstname, TA.lastname, Pt.post_no '
                                'FROM TA, TA_teach TT, Posts Pt, TA P, Sections Sec '
                                'WHERE ? = P.semail AND P.semail = TT.semail AND TT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND TT.semail = TA.semail;',
                                (myid,))
    forumT = cursor.fetchall()
    cursor = connection.execute('SELECT DISTINCT Pt.cid, Pt.ptitle, P2.firstname, P2.lastname, Pt.post_no '
                                'FROM Professors P2, TA_teach TT, Posts Pt, TA P, Sections Sec '
                                'WHERE ? = P.semail AND P.semail = TT.semail AND TT.teaching_team_id = Sec.teaching_team_id '
                                'AND Sec.cid = Pt.cid AND TT.semail = P2.pemail;',
                                (myid,))
    forumP = cursor.fetchall()
    tempforum = []
    for set in forumS:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forumT:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    for set in forumP:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4]])
    if request.method == 'POST':
        global temppostnum
        temppostnum = request.form['postnum']
        return redirect('/commentTATA')
    if tempforum:
        return render_template('forumTATA.html', error=error, forum=tempforum)
    else:
        error = 'invalid input name'
    return render_template('forumTATA.html', error=error)


@app.route('/createforumTATA', methods=['POST', 'GET'])
def createforumTATA():
    error = None
    connection = sql.connect('database.db')
    cursor1 = connection.execute('SELECT DISTINCT Sec.cid  '
                                 'FROM TA P, TA_teach Pt, Sections Sec '
                                 'WHERE ? = P.semail AND ? = P.Password AND P.semail = Pt.semail AND Pt.teaching_team_id = Sec.teaching_team_id',
                                 (myid, mypw))
    myclass = cursor1.fetchall()
    courses = []
    for set in myclass:
        courses.append(set[0])
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")  # when insert
        getcid = request.form['cid']
        gettitle = request.form['title']
        getnote = request.form['note']
        connection.execute(
            'INSERT INTO Posts (semail, cid, pdate, ptime, ptitle, postdesc) VALUES (?,?,?,?,?,?)', (myid, getcid, getdate, gettime, gettitle, getnote))
        connection.commit()
        return redirect('/forumTATA')
    if myclass:
        return render_template('createforumTATA.html', error=error, myclass=courses)
    else:
        error = 'invalid input name'
    return render_template('createforumTATA.html', error=error)


@app.route('/commentTATA', methods=['POST', 'GET'])
def commentTATA():
    error = None
    connection = sql.connect('database.db')
    print(temppostnum)
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, TA S, Students S2 '
        'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.semail',
        (myid, mypw, temppostnum))
    forum = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, TA S, TA S2 '
        'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.semail',
        (myid, mypw, temppostnum))
    forum1 = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Pt.cid, Pt.ptitle, S2.firstname, S2.lastname, Pt.postdesc, Pt.pdate, Pt.ptime '
        'FROM Posts Pt, TA S, Professors S2 '
        'WHERE ? = S.semail AND ? = S.Password AND ? = Pt.post_no AND Pt.semail = S2.pemail',
        (myid, mypw, temppostnum))
    forum2 = cursor1.fetchall()
    tempforum = []
    for set in forum:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum1:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    for set in forum2:
        tempname = set[2] + ' ' + set[3]
        tempforum.append([set[0], set[1], tempname, set[4], set[5], set[6]])
    print(tempforum)
    cursor1 = connection.execute(
        'SELECT DISTINCT Com.pdate, Com.ptime, Students.firstname, Students.lastname, Com.comdesc, Com.post_no '
        'FROM Students, Comments Com '
        'WHERE ? = Com.post_no AND Com.semail = Students.semail;',
        (temppostnum,))
    comment = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Com.pdate, Com.ptime, TA.firstname, TA.lastname, Com.comdesc, Com.post_no '
        'FROM TA, Comments Com '
        'WHERE ? = Com.post_no AND Com.semail = TA.semail;',
        (temppostnum,))
    commentTA = cursor1.fetchall()
    cursor1 = connection.execute(
        'SELECT DISTINCT Com.pdate, Com.ptime, P.firstname, P.lastname, Com.comdesc, Com.post_no '
        'FROM Professors P, Comments Com '
        'WHERE ? = Com.post_no AND Com.semail = P.pemail;',
        (temppostnum,))
    commentP = cursor1.fetchall()
    tempcomment = []
    for set in comment:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    for set in commentTA:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    for set in commentP:
        tempname = set[2] + ' ' + set[3]
        tempcomment.append([set[0], set[1], tempname, set[4]])
    print(cidnum)
    print(temppostnum)
    if request.method == 'POST':
        dateTime = datetime.now()
        getdate = str(dateTime.year) + "/" + \
            str(dateTime.month) + "/" + str(dateTime.day)
        gettime = dateTime.strftime("%H:%M:%S")
        getnote = request.form['com']
        connection.execute(
            'INSERT INTO Comments (cid, post_no, pdate, ptime, semail, comdesc) VALUES (?,?,?,?,?,?)',
            (cidnum, temppostnum, getdate, gettime, myid, getnote))
        connection.commit()
        return redirect('/commentTATA')
    if tempforum:
        return render_template('commentTATA.html', error=error, forum=tempforum, comment=tempcomment)
    else:
        error = 'invalid input name'
    return render_template('commentTATA.html', error=error)


if __name__ == '__main__':
    app.run()
