from datetime import timedelta
from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 15)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
 
#this is the student table of the database
class Student(db.Model):
    __tablename__ = 'Student'
    id = db.Column(db.Integer, primary_key = True)
    utorid = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable = False)
    grades = db.relationship('Grades', backref='student_grades_author', lazy = True)
    remark = db.relationship('Remark', backref='student_remark_author', lazy = True)
    feedback = db.relationship('Feedback', backref='student_feedback_author', lazy = True)

    def __repr__(self):
        return f"Student('{self.utorid}', '{self.email}')"

#this is the instructor table of the database        
class Instructor(db.Model):
    __tablename__ = 'Instructor'
    id = db.Column(db.Integer, primary_key = True)
    utorid = db.Column(db.String(20), unique=True, nullable = False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable = False)
    feedback = db.relationship('Feedback', backref='instructor_feedbackauthor', lazy = True)

    def __repr__(self):
        return f"Instructor('{self.utorid}', '{self.email}')"


#this is the grades table of the database
class Grades(db.Model):
    __tablename__ = 'Grades'
    id = db.Column(db.Integer, primary_key = True)
    a1 = db.Column(db.Integer)
    a2 = db.Column(db.Integer)
    a3 = db.Column(db.Integer)
    midterm = db.Column(db.Integer)
    final = db.Column(db.Integer)
    utorid = db.Column(db.String(20), db.ForeignKey('Student.utorid'), nullable = False)

#this is the remark table of the database
class Remark(db.Model):
    __tablename__ = 'Remark'
    id = db.Column(db.Integer, primary_key = True)
    a1_remark = db.Column(db.String(1000))
    a2_remark = db.Column(db.String(1000))
    a3_remark = db.Column(db.String(1000))
    midterm_remark = db.Column(db.String(1000))
    final_remark = db.Column(db.String(1000))
    utorid = db.Column(db.String(20), db.ForeignKey('Student.utorid'), nullable = False)

#this is the feedback table of the database
class Feedback(db.Model):
    __tablename__ = 'Feedback'
    id = db.Column(db.Integer, primary_key = True)
    q1 = db.Column(db.String(400))
    q2 = db.Column(db.String(400))
    q3 = db.Column(db.String(400))
    q4 = db.Column(db.String(400))
    student_utorid = db.Column(db.String(20), db.ForeignKey('Student.utorid'), nullable = False)
    instructor_utorid = db.Column(db.String(20), db.ForeignKey('Instructor.utorid'), nullable = False)

db.create_all()

#Creating the Sets and filling them with the names already in the DB
student_set = {"student1", "student2"}
instructor_set = {"instructor1", "instructor2"}

#The different pages are all represented here with routes
@app.route('/')
@app.route('/home')
def home():
    pagename = 'home'
    return render_template('index.html', pagename = pagename)

@app.route('/welcome')
def welcome():
    pagename = 'welcome'
    return render_template('home.html', pagename = pagename)

@app.route('/announcements')
def announcements():
    pagename = 'announcements'
    return render_template('announcements.html', pagename = pagename)


@app.route('/assignments')
def assignments():
    pagename = 'assignments'
    return render_template('assignments.html', pagename = pagename)

@app.route('/courseTeam')
def courseTeam():
    pagename = 'courseTeam'
    return render_template('courseTeam.html', pagename = pagename)

@app.route('/labs')
def labs():
    pagename = 'labs'
    return render_template('labs.html', pagename = pagename)

@app.route('/lectureSlides')
def lectureSlides():
    pagename = 'lectureSlides'
    return render_template('lectureSlides.html', pagename = pagename)

@app.route('/markus')
def markus():
    pagename = 'markus'
    return render_template('markus.html', pagename = pagename)

@app.route('/officeHours')
def officeHours():
    pagename = 'officeHours'
    return render_template('officeHours.html', pagename = pagename)

@app.route('/piazza')
def piazza():
    pagename = 'piazza'
    return render_template('piazza.html', pagename = pagename)

@app.route('/syllabus')
def syllabus():
    pagename = 'syllabus'
    return render_template('syllabus.html', pagename = pagename)

#registering a user
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        utorid = request.form['Utorid']
        email = request.form['Email']
        hashed_password = bcrypt.generate_password_hash(request.form['Password']).decode('utf-8')
        #this if is if no radio button was selected
        if 'User' not in request.form:
            flash('Please select either Student or Instructor', 'error')
            return render_template('register.html')
        else:
            user = request.form['User']
            #creates either a student or instructor depending on radio button choice
            if user == 'Student':
                reg_details =(
                    utorid,
                    email,
                    hashed_password
                )
                add_student(reg_details)
                student_set.add(utorid)
                flash('Registration Successful! Please login now:')
                return redirect(url_for('home'))
            elif user == 'Instructor':
                reg_details =(
                    utorid,
                    email,
                    hashed_password
                )
                add_instructor(reg_details)
                instructor_set.add(utorid)
                flash('Registration Successful! Please login now:')
                return redirect(url_for('home'))

#logging in a user and creating a session for them
@app.route('/login', methods = ['GET', 'POST'])
def login():
    #logging in when already logged in
    if request.method == 'GET':
        if 'name' in session:
            flash('already logged in!!')
            return redirect(url_for('home'))
        else:
            return render_template('login.html')
    else:
        utorid = request.form['Utorid']
        password = request.form['Password']
        #if they didn't pick a radio button
        if 'User' not in request.form:
            flash('Please select either Student or Instructor', 'error')
            return render_template('index.html')
        else:
            user = request.form['User']
            #logs in as a student or instructor depending on their radio button choice
            if user == 'Student':
                student = Student.query.filter_by(utorid = utorid).first()
                if not student or not bcrypt.check_password_hash(student.password, password):
                    flash('Please check your login details and try again', 'error')
                    return render_template('index.html')
                else:
                    session['name'] = utorid
                    session.permanent = True
                    return redirect(url_for('welcome'))
            elif user == 'Instructor':
                student = Instructor.query.filter_by(utorid = utorid).first()
                if not student or not bcrypt.check_password_hash(student.password, password):
                    flash('Please check your login details and try again', 'error')
                    return render_template('index.html')
                else:
                    session['name'] = utorid
                    session.permanent = True
                    return redirect(url_for('welcome'))
            

@app.route('/logout')
def logout():
    session.pop('name', default = None)
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    pagename = 'profile'
    #checks the sets that we creates to determine whether or not the user is a student or an instructor. Will have different profile pages
    if(session['name'] in student_set):
        return render_template('profileStudent.html', pagename = pagename)
    else:
        return render_template('profileInstructor.html', pagename = pagename )

@app.route('/remarkInstructor', methods = ['GET', 'POST'])
def instructorRemark():
    if request.method == 'GET':
        query_remark_result = query_remark()
        return render_template('remarkInstructor.html', query_remark_result = query_remark_result)

@app.route('/feedbackInstructor', methods = ['GET', 'POST'])
def instructorFeedback():
    if request.method == 'GET':
        query_feedback_result = query_feedback()
        return render_template('feedbackInstructor.html', query_feedback_result = query_feedback_result)

@app.route('/feedbackStudent', methods = ['GET', 'POST'])
def studentFeedback():
    if request.method == 'GET':
        query_instructor_result = query_instructor()
        return render_template('feedbackStudent.html', query_instructor_result = query_instructor_result)
    else:
        feedback_details =(
            request.form['Instructor_ID'],
            request.form['Q1'],
            request.form['Q2'],
            request.form['Q3'],
            request.form['Q4'],
        )
        add_feedback(feedback_details)
        query_instructor_result = query_instructor()
        return render_template('feedbackStudent.html', query_instructor_result = query_instructor_result)

@app.route('/gradesStudent', methods = ['GET', 'POST'])
def studentGrades():
    if request.method == 'GET':
        query_grades_result = query_grades()
        return render_template('gradesStudent.html', query_grades_result = query_grades_result)
    else:
        remark_details =(
            request.form['A1_remark'],
            request.form['A2_remark'],
            request.form['A3_remark'],
            request.form['Midterm_remark'],
            request.form['Final_remark'],
        )
        add_remark(remark_details)
        query_grades_result = query_grades()
        return render_template('gradesStudent.html', query_grades_result = query_grades_result)

@app.route('/gradesInstructor', methods = ['GET', 'POST'])
def instructorGrades():
    if request.method == 'GET':
        query_grades_result = query_grades()
        return render_template('gradesInstructor.html', query_grades_result = query_grades_result)
    else:
        grade_details =(
            request.form['Student_ID'],
            request.form['A1'],
            request.form['A2'],
            request.form['A3'],
            request.form['Midterm'],
            request.form['Final']
        )
        add_grade(grade_details)
        query_grades_result = query_grades()
        return render_template('gradesInstructor.html', query_grades_result = query_grades_result)
#the add function adds an entry into the database for the specific table
def add_student(reg_details):
    student = Student(utorid = reg_details[0], email = reg_details[1], password = reg_details[2])
    db.session.add(student)
    db.session.commit()

def add_instructor(reg_details):
    student = Instructor(utorid = reg_details[0], email = reg_details[1], password = reg_details[2])
    db.session.add(student)
    db.session.commit()

def add_grade(grade_details):
    grade = Grades(utorid = grade_details[0], a1 = grade_details[1], a2 = grade_details[2], a3 = grade_details[3], midterm = grade_details[4] , final = grade_details[5])
    db.session.add(grade)
    db.session.commit()

def add_feedback(feedback_details):
    feedback = Feedback(instructor_utorid = feedback_details[0], q1 = feedback_details[1], q2 = feedback_details[2], q3 = feedback_details[3], q4 = feedback_details[4] , student_utorid = session['name'])
    db.session.add(feedback)
    db.session.commit()

def add_remark(remark_details):
    remark = Remark(utorid = session['name'], a1_remark = remark_details[0], a2_remark = remark_details[1], a3_remark = remark_details[2], midterm_remark = remark_details[3] , final_remark = remark_details[4])
    db.session.add(remark)
    db.session.commit()

#the query functions get the info from the database (for when we display our data in table form)
def query_grades():
    query_grades = Grades.query.all()
    return query_grades

def query_feedback():
    query_feedback = Feedback.query.all()
    return query_feedback

def query_instructor():
    query_instructor = Instructor.query.all()
    return query_instructor

def query_remark():
    query_remark = Remark.query.all()
    return query_remark

if __name__ == '__main__':
    app.run(debug=True)
