# CMSI-662-HW5
GitHub Repo for HW5 in which we implment a bank webapp.
It is a simple banking web application built with Flask. It allows users to register, login, view account balances, transfer funds between accounts.

## Features

- User authentication: Users can register for an account and log in securely.
- Account management: Users can view their account balances.
- Fund transfers: Users can transfer funds between their accounts or to other users' accounts. There is also validation to prevent transferring from accounts users don't control along with preventing abusing amounts to take money from others.
- Security: The application includes measures to protect against common web security vulnerabilities, such as SQL injection, Cross-Site Scripting (XSS), Cross-Site Request Forgery (CSRF), and User Enumeration attacks.

## Software used

- **Flask**
- **PyJWT**
- **passlib**
- **HTML**
- **Python**
- **SQLite** (OPTIONAL)

## Getting Started

To run the application locally, follow these steps:
1. Clone this repo
2. Open a terminal/command prompt and navigate to that directory
3. Use "python3 -m venv env" to create an environment
4. On Linux, use ". env/bin/activate" or on Windows "env\Scripts\activate.bat" to enter the environment
5. Install required libraries with "pip install Flask Flask-WTF PyJWT passlib"
5.5. (OPTIONAL) Use "export FLASK_ENV=development"
6. Create necessary sql tables with "python3 createdb.py" and "python3 makeaccounts.py"
7. Use "flask run" to create a local server for the webapp (likely located on localhost port 5000, localhost:5000)
