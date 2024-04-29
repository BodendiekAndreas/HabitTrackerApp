README.md

# **Habit Tracker App**

This app aims to provide a platform to create, maintain, and keep track of users' habits. It uses Python's Flask framework and database operations are facilitated using the SQLAlchemy ORM.

## **Requirements**

To install and run this app you will need:

* Python 3.9.19

* SQLite (or any other SQL database you'd like to use)

## **Installation**

Clone the repository to your local machine:

`git clone https://github.com/yourusername/habittracker.git
cd habittracker`

Set up a virtual environment and activate it:

`python3 -m venv venv
source venv/bin/activate   # For Unix or MacOS
venv\Scripts\activate   # For Windows`

Install the required packages:

`pip install -r requirements.txt`

Please note that you'll need to create a requirements.txt file in your repository that lists all the dependencies for your project for this to work. You can do this by running pip freeze > requirements.txt in your project directory.

## Database Setup

First, we need to create the database:

`from app import db db.create_all()`


## Running the Application

Now, you can run your application:

`run.py`

## Running the Tests

We also include a suite of tests for our application. To run the tests:

`pytest`

Your Flask application should now be up and running at localhost:5000. The tests will ensure all the major functionalities of the app are working as expected.
