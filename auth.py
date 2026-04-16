from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Student, Coordinator
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import base64
from flask import make_response


def to_float(value):
    try:
        return float(value)
    except:
        return None


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        role = request.form['role']

        # ---------------- STUDENT LOGIN ----------------
        if role == 'student':
            prn = request.form['prn']
            password = request.form['password']

            student = Student.query.filter_by(prn=prn).first()

            if not student:
                return "Student not registered. Please register first."

            if check_password_hash(student.password, password):
                session.clear()
                session['user'] = 'student'
                session['prn'] = prn
                return redirect('/student/dashboard')

            return "Invalid PRN or Password"

        # ---------------- COORDINATOR LOGIN ----------------
        elif role == 'coordinator':
            username = request.form['username']
            password = request.form['password']

            coordinator = Coordinator.query.filter_by(username=username).first()

            if coordinator and check_password_hash(coordinator.password, password):
                session.clear()
                session['user'] = 'coordinator'
                session['division'] = coordinator.division
                return redirect('/coordinator/dashboard')

            return "Invalid Coordinator Credentials"

    return render_template('login.html')


@auth_bp.route('/student/dashboard')
def student_dashboard():

    if session.get('user') != 'student':
        return redirect('/student/login')

    student = Student.query.filter_by(prn=session['prn']).first()

    return render_template(
        'student_dashboard.html',
        student=student
    )



@auth_bp.route('/coordinator/add_student', methods=['POST'])
def coordinator_add_student():
    if session.get('user') != 'coordinator':
        return redirect('/login')

    prn = request.form['prn']

    if Student.query.filter_by(prn=prn).first():
        return "Student already exists"

    student = Student(
        prn=prn,
        name=request.form['name'],
        division=request.form['division']
    )

    db.session.add(student)
    db.session.commit()

    return "Student added successfully"

@auth_bp.route('/coordinator/view', methods=['POST'])
def view_student():
    if session.get('user') != 'coordinator':
        return redirect('/login')

    prn = request.form['prn']
    division = session['division']

    student = Student.query.filter_by(prn=prn, division=division).first()

    if not student:
        return "Access denied or student not found"

    return render_template('view_student.html', student=student)

# ---------------- STUDENT REGISTRATION FORM ----------------
@auth_bp.route('/student/register', methods=['GET', 'POST'])
def student_register():

    if request.method == 'POST':
        prn = request.form['prn']
        password = request.form['password']

        if Student.query.filter_by(prn=prn).first():
            return "Student already registered. Please login."

        student = Student(
            prn=prn,
            password=generate_password_hash(password)
        )
        db.session.add(student)
        db.session.commit()

        session['user'] = 'student'
        session['prn'] = prn
        return redirect('/student/gfm-form')

    return render_template('student_register.html')


@auth_bp.route('/student/login', methods=['GET', 'POST'])
def student_login():

    if request.method == 'POST':
        prn = request.form['prn']
        password = request.form['password']

        student = Student.query.filter_by(prn=prn).first()

        if not student:
            return "Student not registered"

        if check_password_hash(student.password, password):
            session.clear()
            session['user'] = 'student'
            session['prn'] = prn

            # 🔑 CHECK IF FORM FILLED
            if student.name is None:
                return redirect('/student/gfm-form')
            else:
                return redirect('/student/dashboard')

        return "Invalid credentials"

    return render_template('student_login.html')

@auth_bp.route('/create-coordinator')
def create_coordinator():

    if Coordinator.query.first():
        return "Coordinator already exists"

    coordinator = Coordinator(
        username="coordinator1",
        password=generate_password_hash("admin123"),
        division="SE A"
    )

    db.session.add(coordinator)
    db.session.commit()

    return "Coordinator created successfully"


@auth_bp.route('/coordinator/login', methods=['GET', 'POST'])
def coordinator_login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        coordinator = Coordinator.query.filter_by(username=username).first()

        if not coordinator:
            return "Coordinator not registered"

        if check_password_hash(coordinator.password, password):
            session.clear()
            session['user'] = 'coordinator'
            session['division'] = coordinator.division
            return redirect('/coordinator/dashboard')

        return "Invalid credentials"

    return render_template('coordinator_login.html')



@auth_bp.route('/student/gfm-form', methods=['GET', 'POST'])
def gfm_form():

    if session.get('user') != 'student':
        return redirect('/student/login')

    student = Student.query.filter_by(prn=session['prn']).first()

    if student.name and request.method == 'GET':
        return redirect('/student/dashboard')

    if request.method == 'POST':
        # TEXT DATA
        student.name = request.form['name']
        student.email = request.form['email']
        student.phone = request.form['phone']
        student.gender = request.form['gender']
        student.dob = request.form['dob']
        student.address = request.form['address']
        student.division = request.form['division']
        student.year = request.form['year']

        student.ssc_marks = to_float(request.form.get('ssc_marks'))
        student.hsc_marks = to_float(request.form.get('hsc_marks'))

        student.fe_sem1 = to_float(request.form.get('fe_sem1'))
        student.fe_sem2 = to_float(request.form.get('fe_sem2'))

        student.se_sem1 = to_float(request.form.get('se_sem1'))
        student.se_sem2 = to_float(request.form.get('se_sem2'))

        student.te_sem1 = to_float(request.form.get('te_sem1'))
        student.te_sem2 = to_float(request.form.get('te_sem2'))

        student.be_sem1 = to_float(request.form.get('be_sem1'))
        student.be_sem2 = to_float(request.form.get('be_sem2'))



        # 📸 PHOTO UPLOAD
        photo = request.files['photo']
        if photo:
            filename = secure_filename(session['prn'] + "_" + photo.filename)
            photo.save(os.path.join('uploads', filename))
            student.photo = filename

        db.session.commit()
        return redirect('/student/dashboard')

    return render_template('gfm_form.html')


@auth_bp.route('/coordinator/dashboard')
def coordinator_dashboard():

    if session.get('user') != 'coordinator':
        return redirect('/coordinator/login')

    division = session.get('division')

    students = Student.query.filter_by(division=division).all()

    return render_template(
        'coordinator_dashboard.html',
        students=students,
        division=division
    )


@auth_bp.route('/coordinator/view/<int:student_id>')
def coordinator_view_student(student_id):

    if session.get('user') != 'coordinator':
        return redirect('/coordinator/login')

    student = Student.query.get(student_id)

    if not student:
        return "Student not found"

    return render_template(
        'coordinator_view_student.html',
        student=student
    )


@auth_bp.route('/coordinator/register', methods=['GET', 'POST'])
def coordinator_register():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        division = request.form['division']

        if Coordinator.query.filter_by(username=username).first():
            return "Coordinator already exists"

        coordinator = Coordinator(
            username=username,
            password=generate_password_hash(password),
            division=division
        )

        db.session.add(coordinator)
        db.session.commit()

        return redirect('/coordinator/login')

    return render_template('coordinator_register.html')

@auth_bp.route('/student/edit', methods=['GET', 'POST'])
def student_edit():

    if session.get('user') != 'student':
        return redirect('/student/login')

    student = Student.query.filter_by(prn=session['prn']).first()

    if not student:
        return "Student not found"

    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.phone = request.form['phone']
        student.gender = request.form['gender']
        student.dob = request.form['dob']
        student.address = request.form['address']
        student.division = request.form['division']
        student.year = request.form['year']

        student.ssc_marks = to_float(request.form.get('ssc_marks'))
        student.hsc_marks = to_float(request.form.get('hsc_marks'))

        student.fe_sem1 = to_float(request.form.get('fe_sem1'))
        student.fe_sem2 = to_float(request.form.get('fe_sem2'))

        student.se_sem1 = to_float(request.form.get('se_sem1'))
        student.se_sem2 = to_float(request.form.get('se_sem2'))

        student.te_sem1 = to_float(request.form.get('te_sem1'))
        student.te_sem2 = to_float(request.form.get('te_sem2'))

        student.be_sem1 = to_float(request.form.get('be_sem1'))
        student.be_sem2 = to_float(request.form.get('be_sem2'))


        db.session.commit()
        return redirect('/student/dashboard')

    # ✅ This avoids "student undefined"
    return render_template('gfm_edit.html', student=student)


@auth_bp.route('/coordinator/delete/<int:id>', methods=['POST'])
def delete_student(id):

    if session.get('user') != 'coordinator':
        return redirect('/coordinator/login')

    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()

    return redirect('/coordinator/dashboard')

from flask import make_response, render_template

@auth_bp.route('/coordinator/download/<int:student_id>')
def download_student_profile(student_id):

    if session.get('user') != 'coordinator':
        return redirect('/coordinator/login')

    student = Student.query.get(student_id)

    if not student:
        return "Student not found"

    image_base64 = None
    if student.photo:
        image_base64 = image_to_base64(student.photo)

    html_content = render_template(
        'coordinator_view_student.html',
        student=student,
        image_base64=image_base64,
        download=True
    )

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    response.headers['Content-Disposition'] = (
        f'attachment; filename={student.prn}_GFM_Profile.html'
    )

    return response


def image_to_base64(filename):
    path = os.path.join('uploads', filename)
    with open(path, 'rb') as img:
        return base64.b64encode(img.read()).decode('utf-8')



@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
