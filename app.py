from flask import Flask
from models import db
from auth import auth_bp

app = Flask(__name__)
app.secret_key = "gfm_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

import os
from flask import send_from_directory

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


from flask import render_template

@app.route('/')
def home():
    return render_template('home.html')


import os

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB



if __name__ == "__main__":
    app.run(debug=True)
