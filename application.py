import os
import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, date_conversion, timetable_data, active_transactions, active_reservations, change_date_format

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///lasucursal.db")

# Today's date (global variable)
TODAYS_DATE = datetime.date.today()


@app.route("/")
def index():
    """Shows content of home page"""
    return render_template("index.html")

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buys class packages"""
    if request.method == "POST":

        # Adds new class booking into 'transactions' table
        new_class = db.execute("INSERT INTO transactions (user_id, total_hours, remaining_hours, startdate, expirydate, price) VALUES (:user, :hours, :hours, :startdate, :expirydate, :price)",
                            user=session["user_id"], hours=request.form.get("hours"), startdate=request.form.get("start_date"), expirydate=request.form.get("expirydate"), price=request.form.get("price"))

        # Message that will be present on the screen when we redirect
        flash('Class package purchased. Now book some classes!')

        return redirect("/reserve")

    else:
        # Storing information about the different packages to use in the templates, updating here will update all HTML and JavaScript
        packages = {1: {"price": 6, "expiry": 30}, 4: {"price": 20, "expiry": 30}, 8: {"price": 27, "expiry": 30}}

        # Add 7 days to today for max date in modal pop up
        one_week_later = TODAYS_DATE + datetime.timedelta(days=6)

        # Checks they dont already have active class packages and redirects if necessary
        transactions = active_transactions()
        if transactions == 0:
            return render_template("buy.html", packages=packages, one_week_later=one_week_later, today=TODAYS_DATE)
        else:
            return render_template("blocked.html", message="You already have an active class package. Please book the remaining hours before purchasing a new package.", page="buy" )

@app.route("/home")
@login_required
def home():
    """Shows personal homepage to logged in user"""

    # Looks up user according to user logged in
    user = db.execute("SELECT firstname, countries.name AS country FROM users JOIN countries on users.country_id = countries.id WHERE users.id = :user",
                            user=session["user_id"])
    # Saves variables to put on page
    name = user[0]["firstname"].capitalize()
    country = user[0]["country"]

    # Gets information for "Timetable" section
    timetable_info = timetable_data()
    timetable_week = timetable_info[2]
    timetable_classes = db.execute("SELECT classes.id, classes.date, classes.time, teachers.name AS teacher, styles.name AS styles, classes.spaces FROM classes JOIN teachers ON teachers.id = classes.teacher_id JOIN styles ON styles.id = classes.style_id WHERE date BETWEEN :first_day AND :last_day",
                                    first_day=timetable_info[0], last_day=timetable_info[1])

    # Gives us an array of class IDs of reservations with date from today
    reservation_ids = active_reservations()
    # Looks up class info for upcoming reservations
    class_reservations = db.execute("SELECT date, time, teachers.name AS teacher, styles.name AS style, zoom_link FROM classes JOIN teachers ON teachers.id = classes.teacher_id JOIN styles ON styles.id = classes.style_id WHERE classes.id IN (:reservations)",
                            reservations=reservation_ids)

    # Pulls back info for active packages
    active_packages = active_transactions()

    return render_template("home.html", name=name, country=country, timetable_classes=timetable_classes, week=timetable_week, active_packages=active_packages, reservations=class_reservations, change_date_format=change_date_format)

@app.route("/info")
@login_required
def info():
    """Gives information on class styles"""
    return render_template("info.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure username and password submitted
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("error.html", message="You are missing username and/or password", back="/login")

        # Query database
        rows = db.execute("SELECT * FROM users WHERE username=:username",
                            username=request.form.get("username"))

        # Check someone exists with those details + password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", message="Incorrect username and/or password.", back="/login")

        # Add user to session
        session["user_id"] = rows[0]["id"]

        # Redirect user to member's area
        return redirect('/home')

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to homepage
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure all fields are filled in
        if not request.form.get("firstname") or not request.form.get("surname") or not request.form.get("country") or not request.form.get("username") or not request.form.get("password"):
            return render_template("error.html", message="You are missing details.", back="/register")

        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message="Please make sure your passwords match!", back="/register")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Validate that user doesn't already exist
        if len(rows) >= 1:
            return render_template("error.html", message="This username already exists, please try another one.", back="/register")

        # Create password hash
        hash = generate_password_hash(request.form.get("password"))
        firstname = request.form.get("firstname")
        country = request.form.get("country")

        # Insert new user into database, hashing the password and saving the ID to 'user'
        user = db.execute("INSERT INTO users (username, hash, firstname, surname, country_id) VALUES (:username, :hash, :firstname, :surname, :country_id)",
                                                username=request.form.get("username"), hash=hash, firstname=request.form.get("firstname"), surname=request.form.get("surname"), country_id=request.form.get("country"))

        # Remember which user has logged in
        session["user_id"] = user

        return redirect('/home')

    else:
        # Pull country names from database for select on Register page
        countries = db.execute("SELECT * FROM countries")

        return render_template("register.html", countries=countries)

@app.route("/reserve", methods=["GET", "POST"])
@login_required
def reserve():
    """Books a class for the user"""
    if request.method == "POST":

        # Add reservation of class into reservation table
        db.execute("INSERT INTO reservations (transaction_id, class_id) VALUES (:transaction, :classid)",
                    transaction=request.form.get("transactionID"),classid=request.form.get("classID"))

        # Select active transactions (package) and update remaining hours
        transactions = active_transactions()
        remaining_hours = int(transactions[0]['remaining_hours']) - 1

        db.execute("UPDATE transactions SET remaining_hours = :hours WHERE id=:id",
                    hours=remaining_hours, id=transactions[0]['id'])

        # Takes spaces and minus 1 after reservation taken place
        spaces = int(request.form.get("classSpaces")) - 1

        # Updates classes table so it has one less space in the class
        db.execute("UPDATE classes SET spaces = :spaces WHERE id = :classid",
                    spaces=spaces, classid=request.form.get("classID"))

        # If they're buying their last hour of their package, take them to home
        if remaining_hours == 0:
            flash('Reserved! You have now finished your class package.')
            return redirect("/home")
        else:
            flash('Reserved!')
            return redirect("/reserve")
    else:

        # Calls helper function to bring back transactions where user has remaining classes to book
        transactions = active_transactions()

        # If they don't have an active package, show them a page that tells them they can't reserve
        if transactions == 0:
            return render_template("blocked.html", message="You don't have any active packages. Please buy some more.", page="reserve")
        else:
            # Save variables of active transaction
            package_start_date = transactions[0]["startdate"]
            package_end_date = transactions[0]["expirydate"]
            package_hours = transactions[0]["total_hours"]
            package_remaining_hours = transactions[0]["remaining_hours"]

            # Transaction ID of active package
            transaction_id = transactions[0]["id"]

            # Shows classes available for booking
            classes = db.execute("SELECT classes.id AS id, classes.date, classes.time, teachers.name AS teacher, styles.name AS styles, classes.spaces FROM classes JOIN teachers ON teachers.id = classes.teacher_id JOIN styles ON styles.id = classes.style_id WHERE (date BETWEEN :start_date and :end_date) AND date >= :today AND classes.spaces >= 0",
            start_date = package_start_date, end_date = package_end_date, today = TODAYS_DATE)

            # Calls function to get an array of ID's of user's class reservations from today
            reservations = active_reservations()

            count_date = date_conversion(package_end_date)
            total_days =  count_date - TODAYS_DATE

            return render_template("reserve.html", classes=classes, total_days=total_days.days, hours=package_hours, reservations=reservations, remaining_hours=package_remaining_hours, transaction_id=transaction_id, change_date_format=change_date_format, todays_date=TODAYS_DATE)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()

    return render_template("error.html", message="Look like something's gone wrong.")

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)