# CS50 FINAL PROJECT - DANCE CLASS BOOKING PLATFORM
_Lucy Macartney (London, United Kingdom)_
_Luis Felipe Ceballos Caicedo (Cali, Colombia)_

Our final project is a simulation of an online booking platform and student portal for an online dance school. We have been teaching salsa online during the pandemic, and we wanted to create something that would solve a real-life problem for us.

Our web-based application was built using JavaScript, Python, and SQL, based in part on the web track’s distribution code. We designed the web pages using HTML, CSS and Bootstrap 4.1.

### Index (Landing Page)

One of our goals for the future is to be able to build simple web pages for businesses, so we wanted to challenge ourselves and create a professional landing page for the dance school.

We designed the page using mockups in Canva and then built the page from scratch using HTML, Javascript, CSS and Bootstrap, to bring our designs to life.

## How does the website work?

The basic purpose of the website is to allow users to purchase packages of group classes and then reserve classes according to our timetable and availability. The website also gives the user basic information about the school’s timetable for the week and their upcoming reservations.

### Register

When the user first registers on the site, they are required to enter the following fields:
- First name
- Surname
- Country
- Email: it is checked whether a valid email has been entered and whether this email already has an account
- Password: it is checked to match, and is hashed in the database

The creates a new user in the database, who will be able to login using the “Login” page in the future.

### Buy

On this page, the user can buy different class packages (1 hour, 4 hours or 8 hours). When they click to buy a package, a modal window appears prompting them to choose the start date of their group class package.

The DatePicker only allows the user to choose a start date within the next 7 days, and upon choosing a date, the expiry date field updates dynamically with JavaScript.

### Reserve

On this page, the student is shown which classes are available to book and how many classes they have left in their active class package.

When the student reserves a class:
- The “Book” button will update to “Confirmed” and become inactive
- The number of classes remaining in the package is updated on screen.
- The number of spaces in that class is reduced by 1 and updated in the table.
- If the student books their final hour in their package, they are redirected to the homepage.

### Homepage

This is a client dashboard that shows the following information:
- The user’s first name and country
- A message which changes depending on whether the user has an active class package or not
- A timetable of classes for that week
- Active class reservations for the user (with a button that opens the Zoom meeting for that class)
- A link to a separate page that gives information about all of our class styles

### Database

Our database is made up of 7 tables and stores all users, transactions, classes, teachers, class styles and reservations. Most tables have foreign keys which allow us to join the tables to make queries.

### Date Logic

All parts of the website that are pulling class information from the database are written with logic to not show any classes in the past.

The timetable section on the homepage uses complex date logic to display the upcoming classes for the week (Monday-Friday). We have done some calculations to work out on which day the user is accessing the website, to show the correct classes and to make sure that we aren’t showing any classes in the past.

### Assumptions

The logic of the website is based on the following assumption: the user can only have one active group class package (i.e. with hours remaining). Meaning that the user must reserve all hours in the group class package, or wait until it expires before they can purchase a new one.

Therefore we have built the following validation:
- The BUY page is blocked if the user has an active group package, with a message prompting them to reserve their classes
- The RESERVE page is blocked if the user does not have an active group package, with a message prompting them to buy a new class package.