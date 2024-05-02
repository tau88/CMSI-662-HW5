import sqlite3
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from flask import request, g

import jwt
import time
import random

SECRET = 'yoursupersecrettokenherenumber2'

def get_user_with_credentials(email, password):
    try:
        con = sqlite3.connect('bank.db')
        cur = con.cursor()
        cur.execute('''
            SELECT email, name, password FROM users where email=?''',
            (email,))
        
        #Use a random delay to vary the server response times, preventing user enumeration attacks
            #I decided to use a gaussian curve in order to make it slightly more difficult for
            #attackers to still use high or low rolls to still gain information (my
            #train of logic is that it would take more attempts on the same username before they can
            #be sure that the username is valid/invalid)
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

def logged_in():
    token = request.cookies.get('auth_token')
    try:
        data = jwt.decode(token, SECRET, algorithms=['HS256'])
        g.user = data['sub']
        return True
    except jwt.InvalidTokenError:
        return False

def create_token(email):
    now = datetime.utcnow()
    payload = {'sub': email, 'iat': now, 'exp': now + timedelta(minutes=60)}
    token = jwt.encode(payload, SECRET, algorithm='HS256')
    return token