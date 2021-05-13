from flask import redirect, session
from functools import wraps
import datetime
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///lasucursal.db")

# Today's date
TODAYS_DATE = datetime.date.today()

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Function to change date string to date time object
def date_conversion(date):
    if "-" in date:
        dash = "-"
    (year, month, day) = date.split(dash)
    new_date = datetime.date(int(year), int(month), int(day))
    return new_date

# Function to change dates from YYYY-MM-DD to DD/MM/YYYY
def change_date_format(date):
    if "-" in date:
        dash = "-"
    (year, month, day) = date.split(dash)
    new_date = f"{day}/{month}/{year}"
    return new_date

# Calculates what we should show in our homepage timetable according to today's date
def timetable_data():

    # Gives us all information about todays date
    datetuple = TODAYS_DATE.timetuple()

    # Saving current day of the week
    day_of_week = datetuple[6]

    # Calculating first and last day of the week of classes
    # If it's Monday - Friday
    if day_of_week >= 0 and day_of_week <= 4:
        first_day = TODAYS_DATE
        last_day = TODAYS_DATE + (datetime.timedelta(days=4) - datetime.timedelta(days=day_of_week))
        week = "This"

    # If it's Saturday
    if day_of_week == 5:
        first_day = TODAYS_DATE + datetime.timedelta(days=2)
        last_day = TODAYS_DATE + datetime.timedelta(days=6)
        week = "Next"

    # If it's Sunday
    if day_of_week == 6:
        first_day = TODAYS_DATE + datetime.timedelta(days=1)
        last_day = TODAYS_DATE + datetime.timedelta(days=5)
        week = "Next"

    return(first_day, last_day, week)

def active_transactions():

    # Look up active transactions with classes remaining for user
    transactions = db.execute("SELECT * FROM transactions WHERE user_id = :user AND expirydate >= :today AND remaining_hours > 0",
                                user=session["user_id"], today=TODAYS_DATE)

    # If there aren't any transactions, set to 0
    if len(transactions) == 0:
        transactions = 0

    return transactions

# Finds active class reservations for the user
def active_reservations():

    data = db.execute("SELECT classes.id from users JOIN transactions ON transactions.user_id = users.id JOIN reservations ON transactions.id = reservations.transaction_id JOIN classes ON classes.id = reservations.class_id where users.id=:user AND expirydate >= :today AND classes.date >= :today",
                                user=session["user_id"], today=TODAYS_DATE)
    reservations = []

    for row in data:
        reservations.append(row['id'])

    return reservations