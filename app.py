import os, sqlite3

from flask import Flask, flash, redirect, render_template, request, url_for, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
from passlib.hash import argon2

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure SQLite database
# conn = sqlite3.connect("database.db")
# db = conn.cursor()

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@login_required
def index():
    with sqlite3.connect("database.db") as conn:
        with conn:
            db = conn.cursor()

            if session["role"] == 1:
                tutors_list = []
                tutors = db.execute("SELECT tutor_ids FROM students WHERE id = ?", (session["user_id"],)).fetchall()[0][0]
                if tutors is not None:
                    for i in range(len(tutors)):
                        tutors_list.append(db.execute("SELECT * FROM tutors WHERE id = ?", (int(tutors[i]),)).fetchall())
                    return render_template("index.html", tutors=tutors_list, len=len(tutors_list))
                else:
                    return render_template("index.html")
            else:
                return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        with sqlite3.connect("database.db") as conn:
            with conn:
                db = conn.cursor()

                username = request.form.get("username")
                password = request.form.get("password")

                if not request.form.get("fname"):
                    msg = "Must provide first name"
                    return render_template("error.html", msg=msg)

                elif not request.form.get("lname"):
                    msg = "Must provide last name"
                    return render_template("error.html", msg=msg)

                elif not request.form.get("email"):
                    msg = "Must provide email"
                    return render_template("error.html", msg=msg)

                # Ensure username was submitted
                elif not username:
                    msg = "Must provide username"
                    return render_template("error.html", msg=msg)

                # Ensure password was submitted
                elif not password:
                    msg = "Must provide password"
                    return render_template("error.html", msg=msg)

                # Ensure that password is confirmed
                elif not request.form.get("confirmation"):
                    msg = "Must confirm password"
                    return render_template("error.html", msg=msg)

                # if passwords do not match
                if request.form.get("confirmation") != password:
                    msg = "Passwords do not match"
                    return render_template("error.html", msg=msg)

                if not request.form.get("option"):
                    msg = "Must choose learning status"
                    return render_template("error.html", msg=msg)

                session["user_id"] = 0
                session["role"] = 0

                # Register new user
                if request.form.get("option") == "1":
                    # Query database for email
                    if db.execute("SELECT * FROM students WHERE email = ?", (request.form.get("email"),)).fetchall():
                        msg = "Email already registered"
                        return render_template("error.html", msg=msg)

                    # Query database for username
                    elif db.execute("SELECT * FROM students WHERE username = ?", (username,)).fetchall():
                        msg = "Username already exists"
                        return render_template("error.html", msg=msg)

                    db.execute("INSERT INTO students (fname, lname, email, username, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                        (request.form.get("fname"), request.form.get("lname"), request.form.get("email"), username, argon2.hash(password), request.form.get("option")))

                    # Remember which user has logged in
                    session["user_id"] = db.execute("SELECT id FROM students WHERE username = ?", (username,)).fetchall()[0][0]

                    session["role"] = db.execute("SELECT role FROM students WHERE username = ?", (username,)).fetchall()[0][0]

                elif request.form.get("option") == "2":
                    # Query database for email
                    if db.execute("SELECT * FROM tutors WHERE email = ?", (request.form.get("email"),)).fetchall():
                        msg = "Email already registered"
                        return render_template("error.html", msg=msg)

                    # Query database for username
                    elif db.execute("SELECT * FROM tutors WHERE username = ?", (username,)).fetchall():
                        msg = "Username already exists"
                        return render_template("error.html", msg=msg)

                    db.execute("INSERT INTO tutors (fname, lname, email, username, password, role) VALUES (?, ?, ?, ?, ?, ?)", 
                        (request.form.get("fname"), request.form.get("lname"), request.form.get("email"), username, argon2.hash(password), request.form.get("option")))

                    # Remember which user has logged in
                    session["user_id"] = db.execute("SELECT id FROM tutors WHERE username = ?", (username,)).fetchall()[0][0]

                    session["role"] = db.execute("SELECT role FROM tutors WHERE username = ?", (username,)).fetchall()[0][0]


                # Redirect user to home page
                flash("Registered!")
                return redirect(url_for('index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        with sqlite3.connect("database.db") as conn:
            with conn:
                db = conn.cursor()

                username = request.form.get("email")
                password = request.form.get("password")
            
                # Ensure username was submitted
                if not username:
                    msg = "Must provide username"
                    return render_template("error.html", msg=msg)

                # Ensure password was submitted
                if not password:
                    msg = "Must provide password"
                    return render_template("error.html", msg=msg)

                if not request.form.get("option"):
                    msg = "Must choose learning status"
                    return render_template("error.html", msg=msg)

                rows = ()
                if request.form.get("option") == "1":
                    rows = db.execute("SELECT * FROM students WHERE email = ? OR username = ?", (username, username)).fetchall()

                elif request.form.get("option") == "2":
                    rows = db.execute("SELECT * FROM tutors WHERE email = ? OR username = ?", (username, username)).fetchall()

                # Ensure username exists and password is correct
                if len(rows) != 1 or not argon2.verify(password, rows[0][5]):
                    msg = "Invalid username and/or password"
                    return render_template("error.html", msg=msg)

                # Remember which user has logged in
                session["user_id"] = rows[0][0]
                session["role"] = rows[0][6]

                # Redirect user to home page
                flash("Logged in!")
                return redirect(url_for('index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('index'))

@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings(): 
    """User Settings"""

    with sqlite3.connect("database.db") as conn:
        with conn:
            db = conn.cursor()

            if request.method == "POST":

                if not request.form.get("delete"):
                    
                    # Ensure username was submitted
                    if not request.form.get("password"):
                        msg = "Must provide password"
                        return render_template("error.html", msg=msg)
            
                    # Ensure password was submitted
                    elif not request.form.get("new_password"):
                        msg = "Must provide new password"
                        return render_template("error.html", msg=msg)
            
                    # Ensure that password is confirmed
                    elif not request.form.get("confirm"):
                        msg = "Must confirm password"
                        return render_template("error.html", msg=msg)
            
                    # if passwords do not match
                    if request.form.get("confirm") != request.form.get("new_password"):
                        msg = "Passwords do not match"
                        return render_template("error.html", msg=msg)
                        
                    if session["role"] == 1:
                        # Updates password
                        if argon2.verify(request.form.get("password"), db.execute("SELECT password FROM students WHERE id = ?", (session["user_id"],)).fetchall()[0][0]):
                            db.execute("UPDATE students SET password = ? WHERE id = ?", (argon2.hash(request.form.get("new_password")), session["user_id"]))
                        # if password is incorrect
                        else:
                            msg = "Incorrect password"
                            return render_template("error.html", msg=msg)

                    if session["role"] == 2:
                        # Updates password
                        if argon2.verify(request.form.get("password"), db.execute("SELECT tutors FROM students WHERE id = ?", (session["user_id"],)).fetchall()[0][0]):
                            db.execute("UPDATE tutors SET password = ? WHERE id = ?", (argon2.hash(request.form.get("new_password")), session["user_id"]))
                        # if password is incorrect
                        else:
                            msg = "Incorrect password"
                            return render_template("error.html", msg=msg)
                    
                    # Redirect user to home page
                    flash("Password Changed Succesfully!")
                    return redirect(url_for('index'))
                    
                else:
                    
                    # Delete user from database
                    if session["role"] == 1:
                        db.execute("DELETE FROM students WHERE id = ?", (session["user_id"],))

                    elif session["role"] == 2:
                        db.execute("DELETE FROM tutors WHERE id = ?", (session["user_id"],))
                    
                    # Redirect user to login form
                    session.clear()
                    return redirect(url_for('login'))
                
            else:

                if session["role"] == 1:
                    username = db.execute("SELECT username FROM students WHERE id = ?", (session["user_id"],)).fetchall()[0][0]
                    return render_template("settings.html", username=username)

                elif session["role"] == 2:
                    username = db.execute("SELECT username FROM tutors WHERE id = ?", (session["user_id"],)).fetchall()[0][0]
                    return render_template("settings.html", username=username)

@app.route("/about")
@login_required
def about():
    """About page"""
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact(): 
    """Contact form"""
    with sqlite3.connect("database.db") as conn:
        with conn:
            db = conn.cursor()

            if request.method == "POST":
               return redirect("/confirmation")

            else:
                return render_template('contact.html')

@app.route("/confirmation")
@login_required
def confirmation():
    """Confirm message sent"""
    return render_template("confirmation.html")

@app.route("/tutors", methods=["GET", "POST"])
@login_required
def tutors(): 
    """Show list of tutors"""
    with sqlite3.connect("database.db") as conn:
        with conn:
            db = conn.cursor()

            if request.method == "POST":
                student_ids = db.execute("SELECT student_ids FROM tutors WHERE id = ?", (int(request.form.get("apply")),)).fetchall()[0][0]
                tutor_ids = db.execute("SELECT tutor_ids FROM students WHERE id = ?", (session["user_id"],)).fetchall()[0][0]
                if student_ids is None:
                    db.execute("UPDATE tutors SET student_ids = ? WHERE id = ?", (str(session["user_id"]), int(request.form.get("apply"))))
                if tutor_ids is None:
                    db.execute("UPDATE students SET tutor_ids = ? WHERE id = ?", (request.form.get("apply"), session["user_id"]))
                if student_ids is not None:
                    new_student_ids = student_ids + str(session["user_id"])
                    db.execute("UPDATE tutors SET student_ids = ? WHERE id = ?", (new_student_ids, int(request.form.get("apply"))))
                if tutor_ids is not None:
                    new_tutor_ids = tutor_ids + request.form.get("apply")
                    db.execute("UPDATE students SET tutor_ids = ? WHERE id = ?", (new_tutor_ids, session["user_id"]))

                return redirect(url_for('index'))

            else:
                tutors = db.execute("SELECT * FROM tutors").fetchall()
                return render_template('tutors.html', tutors=tutors, len=len(tutors))

@app.route("/students", methods=["GET", "POST"])
@login_required
def students(): 
    """Show list of students"""
    with sqlite3.connect("database.db") as conn:
        with conn:
            db = conn.cursor()

            students_list = []
            students = db.execute("SELECT student_ids FROM tutors WHERE id = ?", (session["user_id"],)).fetchall()[0][0]
            if students is not None:
                for i in range(len(students)):
                    students_list.append(db.execute("SELECT * FROM students WHERE id = ?", (int(students[i]),)).fetchall())
                return render_template("students.html", students=students_list, len=len(students_list))
            else:
                return render_template("students.html")


# if __name__ == '__main__':
#     app.run(host='127.0.0.1', port=5000)