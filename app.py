import os
from flask import Flask, send_from_directory, render_template
from models import db
from auth import auth_bp

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "gfm_secret_key")

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/')
def home():
    return render_template('home.html')


app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB

if __name__ == "__main__":
    app.run(debug=True)
