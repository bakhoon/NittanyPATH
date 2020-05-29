import csv
import sqlite3 as sql
from datetime import datetime
import hashlib


def get_data():
    #for student table
    connection = sql.connect("database.db")
    cursor = connection.cursor()
    cursor.execute('drop table if exists Students')
    cursor.execute('CREATE TABLE IF NOT EXISTS Students(semail VARCHAR(8) NOT NULL PRIMARY KEY, password TEXT NOT NULL, honorific VARCHAR(4), firstname VARCHAR(16) NOT NULL, '
                   'lastname VARCHAR(16) NOT NULL, degree VARCHAR(4), generation VARCHAR(4), age INTEGER, gender VARCHAR(4), major VARCHAR(6), street VARCHAR(50), phone VARCHAR(16), '
                   'zipcode INTEGER);')
    student = csv.reader(open("Students_TA.csv", "r"))
    for row1 in student:
        if row1[47] != '' or row1[0] == 'Full Name':
            pass
        else:
            get_honorific = None
            get_fname = None
            get_lname = None
            get_degree = None
            get_others = None
            get_id = row1[1].split('@')
            get_name = row1[0].split()
            get_number = str(row1[4])
            get_phone = '(' + get_number[0:3] + ')' + get_number[3:6] + '-' + get_number[6:10]
            if len(get_name) > 2:
                if get_name[0] == 'Mr.' or get_name[0] == 'Mrs.' or get_name[0] == 'Miss' or get_name[0] == 'Ms.' or get_name[0] == 'Dr.':
                    get_honorific = get_name[0]
                    get_fname = get_name[1]
                    get_lname = get_name[2]
                elif get_name[2] == 'PhD' or get_name[2] == 'MD' or get_name[2] == 'MD' or get_name[2] == 'DDS' or get_name[2] == 'DVM':
                    get_degree = get_name[2]
                    get_fname = get_name[0]
                    get_lname = get_name[1]
                elif get_name[2] == 'Sr.' or get_name[2] == 'Jr.' or get_name[2] == 'I' or get_name[2] == 'II' or get_name[2] == 'III' or get_name[2] == 'IV' or get_name[2] == 'V':
                    get_others = get_name[2]
                    get_fname = get_name[0]
                    get_lname = get_name[1]
            else:
                get_fname = get_name[0]
                get_lname = get_name[1]

            pwhashed = hashlib.md5()
            pwhashed.update(row1[8].encode('utf8'))
            secretp = pwhashed.hexdigest()

            database = [get_id[0], secretp, get_honorific, get_fname, get_lname, get_degree, get_others, row1[2], row1[5], row1[10], get_phone, row1[9], row1[3]]
            cursor.execute("INSERT INTO Students(semail, password, honorific, firstname, lastname, degree, generation, age, gender, major, phone, street, zipcode) "
                           "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);", database)
            connection.commit()
    print("Students table is completed.")


    # for TA table
    cursor.execute('drop table if exists TA')
    cursor.execute('CREATE TABLE IF NOT EXISTS TA(semail VARCHAR(8) NOT NULL PRIMARY KEY, password VARCHAR(16) NOT NULL, honorific VARCHAR(4), firstname VARCHAR(16) NOT NULL, '
                   'lastname VARCHAR(16) NOT NULL, degree VARCHAR(4), generation VARCHAR(4), age INTEGER, gender VARCHAR(4), major VARCHAR(6), street VARCHAR(50), phone VARCHAR(16), '
                   'zipcode INTEGER, teachingID INTEGER);')
    student = csv.reader(open("Students_TA.csv", "r"))
    for row in student:
        if row[47] == '' or row[0] == 'Full Name':
            pass
        else:
            get_honorific = None
            get_fname = None
            get_lname = None
            get_degree = None
            get_others = None
            get_id = row[1].split('@')
            get_name = row[0].split()
            get_number = str(row[4])
            get_phone = '(' + get_number[0:3] + ')' + get_number[3:6] + '-' + get_number[6:10]
            if len(get_name) > 2:
                if get_name[0] == 'Mr.' or get_name[0] == 'Mrs.' or get_name[0] == 'Miss' or get_name[0] == 'Ms.' or get_name[0] == 'Dr.':
                    get_honorific = get_name[0]
                    get_fname = get_name[1]
                    get_lname = get_name[2]
                elif get_name[2] == 'PhD' or get_name[2] == 'MD' or get_name[2] == 'MD' or get_name[2] == 'DDS' or get_name[2] == 'DVM':
                    get_degree = get_name[2]
                    get_fname = get_name[0]
                    get_lname = get_name[1]
                elif get_name[2] == 'Sr.' or get_name[2] == 'Jr.' or get_name[2] == 'I' or get_name[2] == 'II' or get_name[2] == 'III' or get_name[2] == 'IV' or get_name[2] == 'V':
                    get_others = get_name[2]
                    get_fname = get_name[0]
                    get_lname = get_name[1]
            else:
                get_fname = get_name[0]
                get_lname = get_name[1]
            pwhashed = hashlib.md5()
            pwhashed.update(row[8].encode('utf8'))
            secretp = pwhashed.hexdigest()
            database = [get_id[0], secretp, get_honorific, get_fname, get_lname, get_degree, get_others, row[2], row[5], row[10], get_phone, row[9], row[3], row[47]]
            cursor.execute(
                "INSERT INTO TA(semail, password, honorific, firstname, lastname, degree, generation, age, gender, major, phone, street, zipcode, teachingID) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?);", database)
            connection.commit()
    print("TA table is completed.")

    #for zipcode student table
    cursor.execute('drop table if exists Zipcodes')
    cursor.execute('CREATE TABLE IF NOT EXISTS Zipcodes(zipcode INTEGER NOT NULL PRIMARY KEY, city VARCHAR(20), '
                   'FOREIGN KEY(zipcode) REFERENCES Students ON DELETE CASCADE);')
    reader = csv.reader(open("Students_TA.csv", "r"))
    zips = []
    for row in reader:
        if row[3] == 'Zip' :
            pass
        else:
            if row[3] in zips:
                pass
            else:
                database = [row[3], row[6]]
                zips.append(row[3])
                cursor.execute(
                    "INSERT INTO Zipcodes(zipcode, city) VALUES (?,?);", database)
                connection.commit()
    print("Zipcodes table is completed.")

    #for cities table
    cursor.execute('drop table if exists Cities')
    cursor.execute('CREATE TABLE IF NOT EXISTS Cities(city VARCHAR(20) NOT NULL PRIMARY KEY, state VARCHAR(16), '
                   'FOREIGN KEY (city) REFERENCES Zipcodes ON DELETE CASCADE);')
    reader = csv.reader(open("Students_TA.csv", "r"))
    zips = []
    for row in reader:
        if row[3] == 'Zip':
            pass
        else:
            if row[6] in zips:
                pass
            else:
                database = [row[6], row[7]]
                zips.append(row[6])
                cursor.execute(
                    "INSERT INTO Cities(city, state) VALUES (?,?);", database)
                connection.commit()
    print("Cities table is completed.")

    #for professors table
    cursor.execute('drop table if exists Professors')
    cursor.execute('CREATE TABLE IF NOT EXISTS Professors(pemail VARCHAR(8) NOT NULL PRIMARY KEY, password VARCHAR(16) NOT NULL, firstname VARCHAR(16) NOT NULL, '
                   'lastname VARCHAR(16) NOT NULL, age INTEGER, gender VARCHAR(4), office_building VARCHAR(3), office_num VARCHAR(16), did VARCHAR(5), '
                   'title VARCHAR(16));')
    reader = csv.reader(open("Professors.csv", "r"))
    for row in reader:
        if row[0] == 'Name':
            pass
        else:
            get_name = row[0].split()
            get_id = row[1].split('@')
            get_office = row[6].split(', ')
            pwhashed = hashlib.md5()
            pwhashed.update(row[2].encode('utf8'))
            secretp = pwhashed.hexdigest()
            database = [get_id[0], secretp, get_name[1], get_name[2], row[3], row[4], get_office[0], get_office[1], row[5], row[8]]
            cursor.execute(
                "INSERT INTO Professors(pemail, password, firstname, lastname, age, gender, office_building, office_num, did, title) "
                "VALUES (?,?,?,?,?,?,?,?,?,?);", database)
            connection.commit()
    print("Professors table is completed.")

    #for departments table
    cursor.execute('drop table if exists Departments')
    cursor.execute('CREATE TABLE IF NOT EXISTS Departments(did VARCHAR(5) NOT NULL PRIMARY KEY, dname VARCHAR(36), head_email VARCHAR(8), UNIQUE(did));')
    reader = csv.reader(open("Professors.csv", "r"))
    dept = []
    title = None
    for row in reader:
        if row[0] == 'Name':
            pass
        else:
            if row[5] in dept:
                pass
            else:
                get_id = row[1].split('@')
                if row[8] == 'Head':
                    database = [row[5], row[7], get_id[0]]
                    dept.append(row[5])
                cursor.execute(
                    "INSERT INTO Departments(did, dname, head_email) VALUES (?,?,?);", database)
                connection.commit()
    print("Departments table is completed.")

    #for semester table
    cursor.execute('drop table if exists Semesters')
    cursor.execute('CREATE TABLE IF NOT EXISTS Semesters(semid INTEGER NOT NULL PRIMARY KEY, years INTEGER, semester VARCHAR(8), '
                   'starts DATE, ends DATE, dropdate DATE, UNIQUE(semid));')
    reader = csv.reader(open("Semester.csv", "r"))
    for row in reader:
        if row[0] == 'Year':
            pass
        else:
            database = [row[2], row[0], row[1], row[3], row[4], row[5]]
            cursor.execute(
                "INSERT INTO Semesters(semid, years, semester, starts, ends, dropdate) VALUES (?,?,?,?,?,?);", database)
            connection.commit()
    print("Semesters table is completed.")

    # for courses table
    cursor.execute('drop table if exists Courses')
    cursor.execute('CREATE TABLE IF NOT EXISTS Courses(cid VARCHAR(12) PRIMARY KEY, cname VARCHAR(49), cdesc VARCHAR(99), semid INTEGER, '
                   'FOREIGN KEY (semid) REFERENCES Semesters ON DELETE CASCADE);')
    reader = csv.reader(open("Students_TA.csv", "r"))
    courses = []
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if row[11] in courses:
                pass
            else:
                database = [row[11], row[12], row[13], row[14]]
                courses.append(row[11])
                cursor.execute(
                    "INSERT INTO Courses(cid, cname, cdesc, semid) VALUES (?,?,?,?);", database)
                connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if row[23] in courses:
                pass
            else:
                database = [row[23], row[24], row[25], row[26]]
                courses.append(row[23])
                cursor.execute(
                    "INSERT INTO Courses(cid, cname, cdesc, semid) VALUES (?,?,?,?);", database)
                connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if row[35] in courses:
                pass
            else:
                database = [row[35], row[36], row[37], row[38]]
                courses.append(row[35])
                cursor.execute(
                    "INSERT INTO Courses(cid, cname, cdesc, semid) VALUES (?,?,?,?);", database)
                connection.commit()
    print("Courses table is completed.")

    #got the row from top
    def get_teaching():
        teach = None
        reader2 = csv.reader(open("Professors.csv", "r"))
        for subrow in reader2:
            if subrow[10] == row[11]:
                teach = subrow[9]
                break
        return teach

    #for section table
    cursor.execute('drop table if exists Sections')
    cursor.execute('CREATE TABLE IF NOT EXISTS Sections(cid VARCHAR(12), sec_no INTEGER, lim INTEGER, teaching_team_id INTEGER,'
                   'FOREIGN KEY (cid) REFERENCES Courses ON DELETE CASCADE);')
    reader = csv.reader(open("Students_TA.csv", "r"))
    sections = []
    teach = None
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if [row[11], row[15]] in sections:
                pass
            else:
                teach = get_teaching()
                database = [row[11], row[15], row[16], teach]
                sections.append([row[11], row[15]])
                cursor.execute(
                    "INSERT INTO Sections(cid, sec_no, lim, teaching_team_id) VALUES (?,?,?,?);", database)
                connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if [row[23], row[27]] in sections:
                pass
            else:
                teach = get_teaching()
                database = [row[23], row[27], row[28], teach]
                sections.append([row[23], row[27]])
                cursor.execute(
                    "INSERT INTO Sections(cid, sec_no, limit, teaching_team_id) VALUES (?,?,?,?);", database)
                connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if [row[35], row[39]] in sections:
                pass
            else:
                teach = get_teaching()
                database = [row[35], row[39], row[40], teach]
                sections.append([row[35], row[39]])
                cursor.execute(
                    "INSERT INTO Sections(cid, sec_no, limit, teaching_team_id) VALUES (?,?,?,?);", database)
                connection.commit()
    print("Sections table is completed.")

    # for Enrolls table
    cursor.execute('drop table if exists Enrolls')
    cursor.execute('CREATE TABLE IF NOT EXISTS Enrolls(semail VARCHAR(8), cid VARCHAR(12), sec_no INTEGER, FOREIGN KEY (semail) REFERENCES Posts ON DELETE CASCADE);')
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[11], row[15]]
            cursor.execute(
                "INSERT INTO Enrolls(semail, cid, sec_no) VALUES (?,?,?);", database)
            connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[23], row[27]]
            cursor.execute(
                "INSERT INTO Enrolls(semail, cid, sec_no) VALUES (?,?,?);", database)
            connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[35], row[39]]
            cursor.execute(
                "INSERT INTO Enrolls(semail, cid, sec_no) VALUES (?,?,?);", database)
            connection.commit()
    print("Enrolls table is completed.")

    #for TA-teach table
    cursor.execute('drop table if exists TA_teach')
    cursor.execute('CREATE TABLE IF NOT EXISTS TA_teach(semail VARCHAR(8), teaching_team_id INTEGER);')
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[47] == '' or row[0] == 'Full Name':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[47]]
            cursor.execute(
                "INSERT INTO TA_teach(semail, teaching_team_id) VALUES (?,?);", database)
            connection.commit()
    print("TA_teach table is completed.")

    #for professor-teach table
    cursor.execute('drop table if exists Professor_teach')
    cursor.execute('CREATE TABLE IF NOT EXISTS Professor_teach(pemail VARCHAR(8), teaching_team_id INTEGER);')
    reader = csv.reader(open("Professors.csv", "r"))
    for row in reader:
        if row[0] == 'Name':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[9]]
            cursor.execute(
                "INSERT INTO Professor_teach(pemail, teaching_team_id) VALUES (?,?);", database)
            connection.commit()
    print("Professor_teach table is completed.")

    #for homework table
    cursor.execute('drop table if exists Homeworks')
    cursor.execute('CREATE TABLE IF NOT EXISTS Homeworks(cid VARCHAR(12), sec_no INTEGER, hw_no INTEGER, hwdesc VARCHAR(99));')
    homeworks = []
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if [row[11], row[15], row[17]] in homeworks:
                pass
            else:
                database = [row[11], row[15], row[17], row[18]]
                homeworks.append([row[11], row[15], row[17]])
                cursor.execute(
                    "INSERT INTO Homeworks(cid, sec_no, hw_no, hwdesc) VALUES (?,?,?,?);", database)
                connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if [row[23], row[27], row[29]] in homeworks:
                pass
            else:
                database = [row[23], row[27], row[29], row[30]]
                homeworks.append([row[23], row[27], row[29]])
                cursor.execute(
                    "INSERT INTO Homeworks(cid, sec_no, hw_no, hwdesc) VALUES (?,?,?,?);", database)
                connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if [row[35], row[39], row[41]] in homeworks:
                pass
            else:
                database = [row[35], row[39], row[41], row[42]]
                homeworks.append([row[35], row[39], row[41]])
                cursor.execute(
                    "INSERT INTO Homeworks(cid, sec_no, hw_no, hwdesc) VALUES (?,?,?,?);", database)
                connection.commit()
    print("Homeworks table is completed.")

    #for hw-grade table
    cursor.execute('drop table if exists Homeworks_grade')
    cursor.execute('CREATE TABLE IF NOT EXISTS Homeworks_grade(semail VARCHAR(8), cid VARCHAR(12), sec_no INTEGER, hw_no INTEGER, grade INTEGER,'
                   'FOREIGN KEY (hw_no) REFERENCES Homeworks ON DELETE CASCADE);')
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[11], row[15], row[17], row[19]]
            cursor.execute(
                "INSERT INTO Homeworks_grade(semail, cid, sec_no, hw_no, grade) VALUES (?,?,?,?,?);", database)
            connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[23], row[27], row[29], row[31]]
            cursor.execute(
                "INSERT INTO Homeworks_grade(semail, cid, sec_no, hw_no, grade) VALUES (?,?,?,?,?);", database)
            connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[35], row[39], row[41], row[43]]
            cursor.execute(
                "INSERT INTO Homeworks_grade(semail, cid, sec_no, hw_no, grade) VALUES (?,?,?,?,?);", database)
            connection.commit()
    print("Homeworks_grade table is completed.")

    #for exams table
    cursor.execute('drop table if exists Exams')
    cursor.execute('CREATE TABLE IF NOT EXISTS Exams(cid VARCHAR(12), sec_no INTEGER, exam_no INTEGER, examdesc VARCHAR(99));')
    exams = []
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name':
            pass
        else:
            if [row[11], row[15], row[20]] in exams:
                pass
            else:
                database = [row[11], row[15], row[20], row[21]]
                exams.append([row[11], row[15], row[20]])
                cursor.execute(
                    "INSERT INTO Exams(cid, sec_no, exam_no, examdesc) VALUES (?,?,?,?);", database)
                connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name' or row[32] == '':
            pass
        else:
            if [row[23], row[27], row[32]] in exams:
                pass
            else:
                database = [row[23], row[27], row[32], row[33]]
                exams.append([row[23], row[27], row[32]])
                cursor.execute(
                    "INSERT INTO Exams(cid, sec_no, exam_no, examdesc) VALUES (?,?,?,?);", database)
                connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name' or row[44] == '':
            pass
        else:
            if [row[35], row[39], row[44]] in exams:
                pass
            else:
                database = [row[35], row[39], row[44], row[45]]
                exams.append([row[35], row[39], row[44]])
                cursor.execute(
                    "INSERT INTO Exams(cid, sec_no, exam_no, examdesc) VALUES (?,?,?,?);", database)
                connection.commit()
    print("Exams table is completed.")

    # for exam-grade table
    cursor.execute('drop table if exists Exams_grade')
    cursor.execute('CREATE TABLE IF NOT EXISTS Exams_grade(semail VARCHAR(8), cid VARCHAR(12), sec_no INTEGER, exam_no INTEGER, grade INTEGER,'
                   'FOREIGN KEY (exam_no) REFERENCES Exams ON DELETE CASCADE);')
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name' or row[20] == '':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[11], row[15], row[20], row[22]]
            cursor.execute(
                "INSERT INTO Exams_grade(semail, cid, sec_no, exam_no, grade) VALUES (?,?,?,?,?);", database)
            connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name' or row[32] == '':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[23], row[27], row[32], row[34]]
            cursor.execute(
                "INSERT INTO Exams_grade(semail, cid, sec_no, exam_no, grade) VALUES (?,?,?,?,?);", database)
            connection.commit()
    reader = csv.reader(open("Students_TA.csv", "r"))
    for row in reader:
        if row[0] == 'Full Name' or row[44] == '':
            pass
        else:
            get_id = row[1].split('@')
            database = [get_id[0], row[35], row[39], row[44], row[46]]
            cursor.execute(
                "INSERT INTO Exams_grade(semail, cid, sec_no, exam_no, grade) VALUES (?,?,?,?,?);", database)
            connection.commit()
    print("Exams_grade table is completed.")

    # for posts table
    cursor.execute('drop table if exists Posts')
    cursor.execute('CREATE TABLE IF NOT EXISTS Posts(post_no INTEGER PRIMARY KEY AUTOINCREMENT, cid VARCHAR(12), pdate TEXT, ptime TEXT, ptitle VARCHAR(50), semail VARCHAR(8), postdesc TEXT, '
                   'FOREIGN KEY (semail) REFERENCES Enrolls ON DELETE CASCADE);')
    reader = csv.reader(open("Posts_Comments.csv", "r"))
    dateTime = datetime.now()
    for row in reader:
        if row[0] == 'Courses' or row[2] == '':
            pass
        else:
            get_id = row[4].split('@')
            getdate = str(dateTime.year) + "/" + str(dateTime.month) + "/" + str(dateTime.day)
            gettime = dateTime.strftime("%H:%M:%S")
            database = [row[0], get_id[0], row[2], row[3], getdate, gettime]
            cursor.execute(
                "INSERT INTO Posts(cid, semail, ptitle, postdesc, pdate, ptime) VALUES (?,?,?,?,?,?);", database)
            connection.commit()
    print("Posts table is completed.")

    #for comment table
    cursor.execute('drop table if exists Comments')
    cursor.execute('CREATE TABLE IF NOT EXISTS Comments(cid VARCHAR(12), post_no INTEGER, semail VARCHAR(8), comdesc VARCHAR(99), pdate TEXT, ptime TEXT,'
                   'FOREIGN KEY (post_no) REFERENCES Posts ON DELETE CASCADE);')
    reader = csv.reader(open("Posts_Comments.csv", "r"))
    dateTime = datetime.now()
    for row in reader:
        if row[0] == 'Courses' or row[4] == '':
            pass
        else:
            get_id = row[7].split('@')
            getdate = str(dateTime.year) + "/" + str(dateTime.month) + "/" + str(dateTime.day)
            gettime = dateTime.strftime("%H:%M:%S")
            database = [row[0], get_id[0], row[6], row[5], getdate, gettime]
            cursor.execute(
                "INSERT INTO Comments(cid, semail, comdesc, post_no, pdate, ptime) VALUES (?,?,?,?,?,?);", database)
            connection.commit()
    print("Comment table is completed.")

    # for appointment table
    cursor.execute('drop table if exists Appointment')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Appointment(semail TEXT, adate TEXT, atime TEXT, note TEXT, title TEXT, witheamil TEXT);')

    # for Message table
    cursor.execute('drop table if exists Message')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Message(sendby TEXT, receiveby TEXT, adate TEXT, atime TEXT, title TEXT, note TEXT);')

    # for posts table
    cursor.execute('drop table if exists Announcements')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS Announcements(anno_no INTEGER PRIMARY KEY AUTOINCREMENT, cid VARCHAR(12), pdate TEXT, ptime TEXT, ptitle VARCHAR(50), pemail VARCHAR(8), postdesc TEXT);')
    print("Announcements table is completed.")

    print("Data is uploaded from Excel file.")

get_data()