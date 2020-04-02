# auth.py

from flask import Blueprint
from flask import Flask, request, render_template, jsonify
from string import ascii_letters, digits
from extensions import mysql


auth_app = Blueprint('auth_app', __name__)


# create_user: (api)
# 
# Frontend "create user" connects directly to this.
# The frontend is responsible for creating salt.
# TODO: This should require email verification.
#
@auth_app.route('/create-user', methods=['POST'])
def create_user():
    # Get user inputs
    email = request.form.get('email')
    username = request.form.get('username')
    passhash = request.form.get('passhash')  # Bcrypt
    salt = request.form.get('salt')

    # TODO: Get automatic inputs (location, device, etc) needs interaction from frontends
    ip = request.remote_addr

    # Cursor
    cur = mysql.get_db().cursor()

    # TODO: Make sure email is a valid email

    # Validate inputs, just check they don't already exist. Password will be checked by frontends
    cur.execute("SELECT username FROM users WHERE username = '%s' OR email = '%s';" % (username, email))
    if cur.rowcount >= 1:
        return "Username or email already exists!"  # This will eventually just return some structure which says this. 

    # Add user to database
    cur.execute("INSERT INTO users (username, email, passhash, salt, verified) VALUES ('%s', '%s', '%s', '%s', false);" % (username, email, passhash, salt))
    mysql.get_db().commit()

    # Craft response
    response = jsonify({'token': 'dummy-token'})
    return "<h1>Welcome, %s </h1>" % username  # This will return a success, as well as an authentication token


# get_salt: (api)
#
# This is recieved after login button on frontend,
# but before the validation.
# If this fails, we will return a "user doesn't exist error"
#
@auth_app.route('/get-salt', methods=['POST'])
def get_salt():
    # Get username
    username = request.form.get('username')
    email = request.form.get('username')

    # Cursor
    cur = mysql.get_db().cursor()

    # Get salt
    cur.execute("SELECT salt FROM users WHERE username = '%s' OR email = '%s';" % (username, email))
    if cur.rowcount < 1:
       return "No such user"
    salt = cur.fetchall()[0]

    # Craft response
    response = jsonify({'salt': salt})
    
    return response


# validate_user: (api)
#
# This is the actual user validation funtion during
# login. This assumes the salt has been gotten by frontend
# already.
#
@auth_app.route('/validate-user', methods=['POST'])
def validate_user():
    # Get user inputs
    username = request.form.get('username')
    email = request.form.get('username')
    passhash = request.form.get('passhash')

    # TODO: Get automatic inputs (location, device, etc)

    # Cursor
    cur = mysql.get_db().cursor()

    # Validate inputs, check username/email exists, check passhash matches
    cur.execute("SELECT userid, username FROM users WHERE (username = '%s' OR email = '%s') AND passhash = '%s';" % (username, email, passhash))
    if cur.rowcount < 1:
        return "Bad username or password"

    # Create auth token
    token = "testtoken"

    # Craft response
    return token


# This is for testing the api. Realistically, you should use Postman
@auth_app.route('/test-auth', methods=['GET'])
def form():

    return '''
            <h2>Test create user</h2>
            <p>This is to create a new user</p>
            <form method="POST" action="/create-user">
                email: <input type="text" name="email"><br>
                username: <input type="text" name="username"><br>
                passhash: <input type="text" name="passhash"><br>
                salt: <input type="text" name="salt"><br>
                <input type="submit" value="Submit"><br>
            </form><br>

            <h2>Test get salt</h2>
            <p>This will be used after user presses login, but before validation</p>
            <form method="POST" action="/get-salt">
                username: <input type="text" name="username"><br>
                <input type="submit" value="Submit"><br>
            </form><br>

            <h2>Test validate user</h2>
            <p>This will be called after the frontend has the salt. The salt and password</p>
            <form method="POST" action="/validate-user">
                username/email: <input type="text" name="username"><br>
                passhash: <input type="text" name="passhash"><br>
                <input type="submit" value="Submit"><br>
            </form><br>
            '''
