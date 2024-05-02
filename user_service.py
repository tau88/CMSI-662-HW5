import sqlite3
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from flask import request, g

import jwt
import time
import random

#Please note that this secret key is a placeholder for uploading to GitHub,
    #the real webapp has a real key.
SECRET = 'yoursupersecrettokenherenumber2'

def get_user_with_credentials(email, password):
    try:
        con = sqlite3.connect('bank.db')
        cur = con.cursor()
        #In the interest of thoroughness, it is worth keeping in mind
            #that these sql queries are more resilient to sql injection due to
            #being parameterized.
        #In a real webapp, there would likely be additional validation on the
            #email field (check if it is a valid email to begin with,
            #such as @ symbol, .com/.org/.edu etc.)
        cur.execute('''
            SELECT email, name, password FROM users where email=?''',
            (email,))
        
        #Use a random delay to vary the server response times, preventing user enumeration attacks
            #I decided to use a gaussian curve in order to make it slightly more difficult for
            #attackers to still use high or low rolls to still gain information (my
            #train of logic is that it would take more attempts on the same username before they can
            #be sure that the username is valid/invalid as their timing could be due to an outlier)
        mean_delay = 0.25       #Mean delay
        std_dev_delay = 0.05    #Standard deviation of the delay
        random_delay =  max(0, random.gauss(mean_delay, std_dev_delay))
        time.sleep(random_delay)
        
        row = cur.fetchone()
        if row is None:
            return None
        email, name, hash = row
        if not pbkdf2_sha256.verify(password, hash):
            return None
        return {"email": email, "name": name, "token": create_token(email)}
    finally:
        con.close()

#Use cookies in order to make sure the user is who they say they are (authentication)
def logged_in():
    token = request.cookies.get('auth_token')
    try:
        data = jwt.decode(token, SECRET, algorithms=['HS256'])
        g.user = data['sub']
        return True
    except jwt.InvalidTokenError:
        return False

#Generate a cookie to allow the webapp to quickly verify that the user is who they
    #say they are (authentication)
def create_token(email):
    now = datetime.utcnow()
    #The cookie has a expiration of 1 hour, this is not common for banking applications
        #which seem to have a logout time of roughly 15 minutes. Either way, this expiry
        #will help avoid attackers from gaining access to the account if the legitimate
        #user wanders off
    payload = {'sub': email, 'iat': now, 'exp': now + timedelta(minutes=60)}
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return token