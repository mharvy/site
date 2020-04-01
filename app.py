from flask import Flask
from auth import auth_app
from extensions import mysql


app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'  # IP of db host
app.config['MYSQL_DATABASE_USER'] = 'testuser'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'userinfo'

app.register_blueprint(auth_app)

mysql.init_app(app)
