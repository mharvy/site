from app import app
from app import db
import bcrypt
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    passhash = db.Column(db.String(60), nullable=False)
    salt = db.Column(db.String(32), nullable=False)
    date_made = db.Column(db.Date(), nullable=False)
    time_made = db.Column(db.Time(), nullable=False)
    verified = db.Column(db.Boolean(), nullable=False)

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        return user

    def generate_auth_token(self, expiration=60*60):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    def verify_password(self, password):
        passhash = bcrypt.hashpw(password, self.salt)
        return passhash == self.passhash


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    userid = db.Column(INTEGER(unsigned=True), nullable=False)
    date_made = db.Column(db.Date(), nullable=False)
    time_made = db.Column(db.Time(), nullable=False)
    clientip = db.Column(db.String(15), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    body = db.Column(TEXT, nullable=False)
    deleted = db.Column(db.Boolean(), nullable=False)
    edited = db.Column(db.Boolean(), nullable=False)


class Comment(db.Model):
    __tablename__ = "comments"
    
    id = db.Column(INTEGER(unsigned=True), primary_key=True, nullable=False)
    submissionid = db.Column(INTEGER(unsigned=True), nullable=False)
    userid = db.Column(INTEGER(unsigned=True), nullable=False)
    parent_comment = db.Column(INTEGER(unsigned=True), nullable=False)
    date_made = db.Column(db.Date(), nullable=False)
    time_made = db.Column(db.Time(), nullable=False)
    clientip = db.Column(db.String(15), nullable=False)
    body = db.Column(TEXT, nullable=False)
    deleted = db.Column(db.Boolean(), nullable=False)
    edited = db.Column(db.Boolean(), nullable=False)