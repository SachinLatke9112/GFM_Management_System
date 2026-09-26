# GFM (Guardian Faculty Member) Management System

A comprehensive, secure, and modern web application built to streamline student data management and faculty mentoring processes for educational institutions.

## 🌟 Key Features

### 🎓 For Students
*   **Secure Registration & Login**: Claim pre-registered accounts and set secure passwords.
*   **Comprehensive Profiles**: Fill out personal details, academic history (SSC, HSC, Semester SGPAs), and upload passport-size photos.
*   **Seamless Profile Management**: Edit and update information dynamically at any time.
*   **Stunning User Interface**: Enjoy a premium, animated "glassmorphism" design system.

### 👨‍🏫 For Coordinators (GFMs)
*   **Analytics Dashboard**: Instantly view division statistics (Total Students, Profile Completion Rates, Gender Ratios).
*   **Student Management**: View detailed academic and personal profiles of assigned students.
*   **Bulk Data Export**: One-click export of the entire division's data into a beautifully formatted CSV file for Excel.
*   **Offline Records**: Download individual student profiles as standalone HTML/PDF documents.

---

## 🛠️ Technology Stack

*   **Backend**: Python, Flask, SQLAlchemy
*   **Database**: SQLite (via SQLAlchemy ORM)
*   **Security**: Werkzeug (Password Hashing, Secure Filenames)
*   **Frontend**: HTML5, CSS3, Bootstrap 5, Jinja2 Templating
*   **Design System**: Custom CSS variables, Google Fonts (Outfit), Bootstrap Icons

---

## 🚀 How to Run Locally

### 1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

### 2. Install Dependencies
Open your terminal and install the required Python packages:
```bash
pip install flask flask-sqlalchemy werkzeug
```

### 3. Run the Application
Navigate to the project directory and start the Flask server:
```bash
python app.py
```

### 4. Access the Portal
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔒 Security Enhancements
This application has been rigorously patched for common web vulnerabilities:
*   **IDOR Protection**: Coordinators can only view and manage students within their explicitly assigned divisions.
*   **Secure File Uploads**: Image uploads are strictly validated against allowed extensions (`.png`, `.jpg`, `.jpeg`, `.gif`).
*   **Password Hashing**: Plain text passwords are never stored; all credentials use salted hashes.
*   **Graceful Error Handling**: Flash messages prevent system information leakage and guide users properly.

---

*Built with ❤️ for Nutan Maharashtra Institute of Engineering & Technology.*
