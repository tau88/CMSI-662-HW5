import sqlite3

def get_balance(account_number, owner):
    try:
        con = sqlite3.connect('bank.db')
        cur = con.cursor()
        
        #In order to ensure authorization, verify that the user is also
            #the owner of the account before allowing them to view it
        #Also, to be thorough, it is worth mentioning that this code is more
            #resilient to SQL injection because it is a parameterized query
        cur.execute('''
            SELECT balance FROM accounts where id=? and owner=?''',
            (account_number, owner))
        row = cur.fetchone()
        if row is None:
            return None
        return row[0]
    finally:
        con.close()

def do_transfer(source, target, amount):
    try:
        con = sqlite3.connect('bank.db')
        cur = con.cursor()
        #Again, in the interest of thoroughness, it is worth keeping in mind
            #that these sql queries are more resilient to sql injection due to
            #being parameterized. Additionally, in the case of the amount field,
            #there is additional validation (in app.py) that checks for an
            #integer-only value, which helps prevent other sql injections if
            #the parameterization is somehow circumvented
        #Also, note that we are only checking that the target field is valid here,
            #this is because the source and amount fields have already been checked
            #by app.py transfer POST call. I believe to do so again would be redundant,
            #which was discussed in an early lecture ("don't be paranoid").
        cur.execute('''
            SELECT id FROM accounts where id=?''',
            (target,))
        row = cur.fetchone()
        if row is None:
            return False
        cur.execute('''
            UPDATE accounts SET balance=balance-? where id=?''',
            (amount, source))
        cur.execute('''
            UPDATE accounts SET balance=balance+? where id=?''',
            (amount, target))
        con.commit()
        return True
    finally:
        con.close()