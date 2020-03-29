#app.py
# This will likely be converted into just the login portion

from flask import Flask, request, render_template, jsonify
from flask_mysqldb import MySQL
from random import choice
from string import ascii_letters, digits


app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'  # IP of db host
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'user_info'

mysql = MySQL(app)


# This is recieved before a login or create_user
@app.route('/get_salt', methods=['POST'])
def get_salt():
    # Get username
    username = request.form.get('username')

    # Cursor
    cur = mysql.connection.cursor()
    print(mysql.connection)

    # Get salt
    cur.execute("SELECT salt FROM users WHERE username = '%s';" % username)
    if cur.rowcount < 1:
        salt = ''.join(choice(ascii_letters + digits) for i in range(20))
    elif cur.rowcount == 1:
        salt = cur.fetchone()[0]

    # Craft response
    response = jsonify({'salt': salt})
    
    return response


# Need to make sure only app/website or whatever can access this api
@app.route('/create_user', methods=['POST'])
def create_user():
    # Get user inputs
    email = request.form.get('email')
    username = request.form.get('username')
    passhash = request.form.get('passhash')  # Bcrypt
    salt = request.form.get('salt')

    # Get automatic inputs (location, device, etc)
    # TODO, needs interaction from frontends

    # Cursor
    cur = mysql.connection.cursor()

    # Validate inputs, just check they don't already exist. Password will be checked by frontends
    cur.execute("SELECT username FROM users WHERE username = '%s' OR email = '%s';" % (username, email))
    if cur.rowcount < 1:
        return "Username or email already exists!"  # This will eventually just return some structure which says this. 

    # Add user to database
    cur.execute("INSERT INTO users (username, email, passhash, salt) VALUES ('%s', '%s', '%s', '%s');" % (username, email, passhash, salt))

    # Craft response
    response = jsonify({'token': 'dummy-token'})
    return "<h1>Welcome, %s </h1>" % username  # This will return a success, as well as an authentication token


@app.route('/validate_user', methods=['POST'])
def validate_user():
    # Get user inputs

    # Get automatic inputs (location, device, etc)

    # Cursor
    cur = mysql.connection.cursor()

    # Validate inputs, check username/email exists, check passhash matches

    # Create token

    # Craft response


# This is for testing the api. Realistically, you should use Postman
@app.route('/test-requests', methods=['GET', 'POST'])
def form():

    return '''
            <p>Test create user</p>
            <form method="POST" action="/create_user">
                email: <input type="text" name="email"><br>
                username: <input type="text" name="username"><br>
                passhash: <input type="text" name="passhash"><br>
                <input type="submit" value="Submit"><br>
            </form>

            <p>Test get salt</p>
            <form method="POST" action="/get_salt">
                username: <input type="text" name="salt"><br>
                <input type="submit" value="Submit"><br>
            </form>
            '''
