# auth.py

from flask import Blueprint
from flask import Flask, request, render_template, jsonify, make_response, g
from datetime import datetime
import bcrypt
from models import User
from app import db, auth


auth_app = Blueprint('auth_app', __name__)


@auth_app.route('/api/auth/signup', methods=['POST'])
def signup():
    # Get user inputs
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    if None in [email, username, password]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # TODO: Get automatic inputs (location, device, etc) needs interaction from frontends
    ip = request.remote_addr
    salt = bcrypt.gensalt()

    # Check if username or email are already used
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Username or email already used.'}))
        return response

    # TODO: Make sure email is a valid email

    # Verify email

    # Add the user to the database
    try:
        # Generate hash
        passhash = str(bcrypt.hashpw(password.encode(encoding='UTF-8'), salt))[2:-1]

        # Add user to database
        new_user = User(username=username, 
                        email=email, 
                        passhash=passhash, 
                        salt=salt, 
                        date_made=datetime.now().strftime('%Y-%m-%d'),
                        time_made=datetime.now().strftime('%H:%M:%S'),
                        verified=False,
                        deleted=False,
                        s_liked="",
                        s_disliked="",
                        c_liked="",
                        c_disliked="")
        db.session.add(new_user)
        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Generate token
    token = new_user.generate_auth_token()
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Logged in.'}))
    response.set_cookie('token', token)
    return response


@auth_app.route('/api/auth/signin', methods=['POST'])
def signin():
    # Get user inputs
    username = request.form.get('username')
    password = request.form.get('password')
    if None in [username, password]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # TODO: Get automatic inputs
    ip = request.remote_addr

    # Get user in question
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User.query.filter_by(email=username).first()
    if not user:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'User does not exist.'}))
        return response

    # Check password
    passhash = str(bcrypt.hashpw(password.encode(encoding='UTF-8'), user.salt.encode(encoding='UTF-8')))[2:-1]
    if passhash != user.passhash:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Wrong password.'}))
        return response

    # Generate token
    token = user.generate_auth_token()
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Signed in.'}))
    response.set_cookie('token', token)
    return response


@auth_app.route('/api/auth/signout', methods=['POST'])
@auth.login_required
def signout():
    # Generate token
    token = g.user.generate_auth_token(expiration=0)
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Signed out.'}))
    response.set_cookie('token', token)
    return response


@auth_app.route('/api/auth/remove', methods=['POST'])
@auth.login_required
def remove_user():
    # Mark user as deleted and remove information
    try:
        user = User.query.filter_by(id=g.user.id).first()
        user.email = None
        user.passhash = None
        user.salt = None
        user.date_made = None
        user.time_made = None
        user.verified = False
        user.deleted = True
        
        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Return success response
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'User deleted.'}))
    return response


# This is for testing the api
@auth_app.route('/api/auth/test', methods=['GET'])
@auth.login_optional
def form():

    user = g.user.username if g.user else "None"

    return '''
            <h2>Signed in as %s<h2><br><br>
            
            <h2>Test create user</h2>
            <form method="POST" action="/api/auth/signup">
                email: <input type="text" name="email"><br>
                username: <input type="text" name="username"><br>
                password: <input type="text" name="password"><br>
                <input type="submit" value="Create user"><br>
            </form><br>

            <h2>Test sign in</h2>
            <form method="POST" action="/api/auth/signin">
                username/email: <input type="text" name="username"><br>
                password: <input type="text" name="password"><br>
                <input type="submit" value="Sign in"><br>
            </form><br>

            <h2>Test sign out</h2>
            <form method="POST" action="/api/auth/signout">
                <input type="submit" value="Sign out"><br>
            </form><br>

            ''' % user
