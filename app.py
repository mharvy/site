from flask import Flask
from extensions import mysql
from api.auth.auth import auth_app
from api.post.post import post_app
from api.comment.comment import comment_app


app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'  # IP of db host
app.config['MYSQL_DATABASE_USER'] = 'testuser'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'maindb'

app.register_blueprint(auth_app)
app.register_blueprint(post_app)
app.register_blueprint(comment_app)

mysql.init_app(app)
