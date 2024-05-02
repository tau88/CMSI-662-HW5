from flask import Flask, request, make_response, redirect, render_template, g, abort
from flask_wtf.csrf import CSRFProtect

from user_service import get_user_with_credentials, logged_in
from account_service import get_balance, do_transfer

app = Flask(__name__)

#As recommended by most security experts, I leave the CSRF protection to an
    #external library instead of implementing it myself. In this case, the
    #CSRFProtect import is used to create a token that will be added to any form
    #in the webapp. This token will be passed into the form automatically (without
    #any action from the user). This will help prevent CSRF attacks as any attacker
    #would be very unlikely to be able to pass the appropriate token in through an
    #external form call.
#Please note that this secret key is a placeholder for uploading to GitHub,
    #the real webapp has a real key.
app.config['SECRET_KEY'] = 'yoursupersecrettokenhere'
csrf = CSRFProtect(app) 

#Using the @app.route template structure from flask helps avoid XSS attacks, as
    #it also includes autoescaping with markupsafe language (Instead of manually adding
    #markupsafe and 'escape([THE STRING])', flask does this for us). 
@app.route("/", methods=['GET'])
def home():
    if not logged_in():
        return render_template("login.html")
    return redirect('/dashboard')

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user = get_user_with_credentials(email, password)
    if not user:
        return render_template("login.html", error="Invalid credentials")
    response = make_response(redirect("/dashboard"))
    
    #This cookie is given to the user's session and will be checked regularly with logged_in
        #(authentication is a high priority validation technique) to ensure only appropriate
        #users are able to see certain webpages
    response.set_cookie("auth_token", user["token"])
    return response, 303
    
@app.route("/dashboard", methods=['GET'])
def dashboard():
    if not logged_in():
        return render_template("login.html")
    return render_template("dashboard.html", email=g.user)

@app.route("/details", methods=['GET'])
def details():
    if not logged_in():
        return render_template("login.html")
    account_number = request.args['account']

    balance = get_balance(account_number, g.user)
    #Instead of remaining on the details page, if the account number is not reachable,
        #return the user to the dashboard page and display an invalid acocunt error
        #message
    #Keep in mind that get_balance will return None both if the account number
        #doesn't exist AND if the user is not authorized to view that account number
    if balance is None:
        return render_template("dashboard.html", error="Invalid account number")
    else:
        return render_template(
            "details.html", 
            user=g.user,
            account_number=account_number,
            balance = get_balance(account_number, g.user))

@app.route("/transfer", methods=["GET"])
def transfer_form():
    if not logged_in():
        return render_template("login.html")
    return render_template("transfer.html")

@app.route("/transfer", methods=["POST"])
def transfer():
    if not logged_in():
        return render_template("login.html")
    source = request.form.get("from")
    target = request.form.get("to")
    amount = request.form.get("amount")

    #Check that the amount input is an integer, this will prevent the 500
        #error seen in class as well as also prevent potential SQL injection
        #by limiting pottential input to only having digits (no <, >, ", /, etc.)
    if not amount.isdigit():
        abort(400, "PLEASE ONLY INPUT INTEGERS")
    else:
        #If the amount indeed only consists of digits, convert the string into int
        amount = int(amount)
        
    #Now that we are fairy certain we are working with an int for amount, validate
        #the amount, such as making sure the amount is non-negative, is not zero, and
        #is not too large (functions like an ATM withdrawl limit)
    if amount == 0:
        abort(400, "DON'T WASTE OUR TIME")
        
    #A side effect of checking for digits also means that '- (negative symbol)' is
        #also caught). I leave this code commented to indicate where this unused code
        #used to be.
    #if amount < 0:
    #    abort(400, "NO STEALING")
    if amount > 1000:
        abort(400, "WOAH THERE TAKE IT EASY")

    #As a reminder, get_balance validates that the user is allowed to access
        #the given account number (source) by checking the owner of said
        #account (authorization). 
    #I bring this up because the transfer form does not validate source as it
        #is validated here instead.
    available_balance = get_balance(source, g.user)
    #If the user does not own the account, the balance will be returned as 'None.'
        #This will lead to a 404 error, which is notable as it is a generic error
        #code, as to avoid giving attackers abusable information such as if an account
        #number exists to begin with (don't disclose too much information).
    if available_balance is None:
        abort(404, "Account not found")
        
    #In this section, check the amount to be transferred against the user's
        #account balance in order to ensure that there is enough money to give
    if amount > available_balance:
        abort(400, "You don't have that much")

    if do_transfer(source, target, amount):
        response = make_response(redirect("/dashboard"))
        return response, 303
    else:
        abort(400, "Something bad happened")

@app.route("/logout", methods=['GET'])
def logout():
    response = make_response(redirect("/dashboard"))
    response.delete_cookie('auth_token')
    return response, 303