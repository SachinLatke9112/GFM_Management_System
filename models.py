from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prn = db.Column(db.String(20), unique=True, nullable=False)

    photo = db.Column(db.String(200))

    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    gender = db.Column(db.String(10))
    dob = db.Column(db.String(20))
    address = db.Column(db.Text)

    division = db.Column(db.String(10))
    year = db.Column(db.String(10))

    ssc_marks = db.Column(db.Float)
    hsc_marks = db.Column(db.Float)

    fe_sem1 = db.Column(db.Float)
    fe_sem2 = db.Column(db.Float)
    se_sem1 = db.Column(db.Float)
    se_sem2 = db.Column(db.Float)
    te_sem1 = db.Column(db.Float)
    te_sem2 = db.Column(db.Float)
    be_sem1 = db.Column(db.Float)
    be_sem2 = db.Column(db.Float)

    password = db.Column(db.String(200))


class Coordinator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    division = db.Column(db.String(10))
