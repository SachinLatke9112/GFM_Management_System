from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Student, Coordinator
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
import os
import base64
import csv
import io
from flask import make_response

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def to_float(value):
    try:
        return float(value)
    except:
        return None


auth_bp = Blueprint('auth', __name__)




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
        return redirect('/coordinator/login')

    prn = request.form['prn']

    if '@' in prn or len(prn) < 5:
        return "Invalid PRN format. Please enter a valid PRN."

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
        return redirect('/coordinator/login')

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

        if '@' in prn or len(prn) < 5:
            flash("Invalid PRN format. Please enter a valid PRN.", "error")
            return redirect('/student/register')

        student = Student.query.filter_by(prn=prn).first()
        if student:
            if student.password:
                flash("Student already registered. Please login.", "warning")
                return redirect('/student/login')
            else:
                student.password = generate_password_hash(password)
        else:
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
            flash("Student not registered", "error")
            return redirect('/student/login')

        if check_password_hash(student.password, password):
            session.clear()
            session['user'] = 'student'
            session['prn'] = prn

            # 🔑 CHECK IF FORM FILLED
            if student.name is None:
                return redirect('/student/gfm-form')
            else:
                return redirect('/student/dashboard')

        flash("Invalid credentials", "error")
        return redirect('/student/login')

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
            flash("Coordinator not registered", "error")
            return redirect('/coordinator/login')

        if check_password_hash(coordinator.password, password):
            session.clear()
            session['user'] = 'coordinator'
            session['division'] = coordinator.division
            return redirect('/coordinator/dashboard')

        flash("Invalid credentials", "error")
        return redirect('/coordinator/login')

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
        student.name = request.form.get('name', '')
        student.email = request.form.get('email', '')
        student.phone = request.form.get('phone', '')
        student.gender = request.form.get('gender', '')
        student.dob = request.form.get('dob', '')
        student.address = request.form.get('address', '')
        student.division = request.form.get('division', '')
        student.year = request.form.get('year', '')

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
        photo = request.files.get('photo')
        if photo and photo.filename != '':
            if allowed_file(photo.filename):
                filename = secure_filename(session['prn'] + "_" + photo.filename)
                photo.save(os.path.join('uploads', filename))
                student.photo = filename
            else:
                return "Invalid file type. Only PNG, JPG, JPEG, GIF are allowed.", 400

        db.session.commit()
        return redirect('/student/dashboard')

    return render_template('gfm_form.html')


@auth_bp.route('/coordinator/dashboard')
def coordinator_dashboard():

    if session.get('user') != 'coordinator':
        return redirect('/coordinator/login')

    division = session.get('division')

    students = Student.query.filter_by(division=division).all()

    total_students = len(students)
    completed_profiles = sum(1 for s in students if s.name)
    male_count = sum(1 for s in students if s.gender == 'Male')
    female_count = sum(1 for s in students if s.gender == 'Female')

    return render_template(
        'coordinator_dashboard.html',
        students=students,
        division=division,
        stats={
            'total': total_students,
            'completed': completed_profiles,
            'male': male_count,
            'female': female_count
        }
    )


@auth_bp.route('/coordinator/view/<int:student_id>')
def coordinator_view_student(student_id):

    if session.get('user') != 'coordinator':
        return redirect('/coordinator/login')

    student = Student.query.get(student_id)

    if not student:
        return "Student not found"
        
    if student.division != session.get('division'):
        return "Unauthorized access to this student", 403

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
            flash("Coordinator already exists", "error")
            return redirect('/coordinator/register')

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
        student.name = request.form.get('name', '')
        student.email = request.form.get('email', '')
        student.phone = request.form.get('phone', '')
        student.gender = request.form.get('gender', '')
        student.dob = request.form.get('dob', '')
        student.address = request.form.get('address', '')
        student.division = request.form.get('division', '')
        student.year = request.form.get('year', '')

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
        photo = request.files.get('photo')
        if photo and photo.filename != '':
            if allowed_file(photo.filename):
                filename = secure_filename(session['prn'] + "_" + photo.filename)
                photo.save(os.path.join('uploads', filename))
                student.photo = filename
            else:
                return "Invalid file type. Only PNG, JPG, JPEG, GIF are allowed.", 400

        db.session.commit()
        return redirect('/student/dashboard')

    # ✅ This avoids "student undefined"
    return render_template('gfm_edit.html', student=student)


@auth_bp.route('/coordinator/delete/<int:id>', methods=['POST'])
def delete_student(id):

    if session.get('user') != 'coordinator':
        return redirect('/coordinator/login')

    student = Student.query.get_or_404(id)
    
    if student.division != session.get('division'):
        return "Unauthorized access to this student", 403

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
        
    if student.division != session.get('division'):
        return "Unauthorized access to this student", 403

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
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as img:
            return base64.b64encode(img.read()).decode('utf-8')
    except Exception:
        return None



@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@auth_bp.route('/coordinator/export')
def export_students():
    if session.get('user') != 'coordinator':
        return redirect('/coordinator/login')

    division = session.get('division')
    students = Student.query.filter_by(division=division).all()

    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow([
        'PRN', 'Name', 'Email', 'Phone', 'Gender', 'DOB', 'Division', 'Year', 'Address', 
        'SSC %', 'HSC %', 'FE Sem1', 'FE Sem2', 'SE Sem1', 'SE Sem2', 'TE Sem1', 'TE Sem2', 'BE Sem1', 'BE Sem2'
    ])
    
    for s in students:
        writer.writerow([
            s.prn, s.name, s.email, s.phone, s.gender, s.dob, s.division, s.year, s.address,
            s.ssc_marks, s.hsc_marks, s.fe_sem1, s.fe_sem2, s.se_sem1, s.se_sem2, s.te_sem1, s.te_sem2, s.be_sem1, s.be_sem2
        ])
    
    from flask import Response
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename=Division_{division}_Students.csv'
    return response

