# Libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Setup app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://testuser:password@localhost/maindb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Setup authentication
app.config['SECRET_KEY'] = 'supersecret'
from extensions import TokenAuth
auth = TokenAuth()


# Register blueprints
from api.auth.auth import auth_app
app.register_blueprint(auth_app)

from api.submission.submission import submission_app
app.register_blueprint(submission_app)

from api.comment.comment import comment_app
app.register_blueprint(comment_app)


# Init
db.create_all(app=app)
db.init_app(app)
