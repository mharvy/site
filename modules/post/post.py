# post.py

from flask import Blueprint
from flask import Flask, request, render_template, jsonify
from string import ascii_letters, digits
from extensions import mysql
from datetime import datetime


post_app = Blueprint('post_app', __name__)


# create_post: (api)
# 
# Frontend "create post" connects directly to this.
# Lol this requires some kind of submission authentication
#
@post_app.route('/post/create', methods=['POST'])
def create_post():
    # Get user inputs
    userid = request.form.get('userid')
    title = request.form.get('title')
    body = request.form.get('body').replace("\"","''")  # This is very patchy

    # Get automatic inputs (ip, date, time, location)
    ip = request.remote_addr
    cur_time = datetime.now().strftime("%H:%M:%S")
    cur_date = datetime.now().strftime("%Y-%m-%d")

    # Cursor
    cur = mysql.get_db().cursor()

    # Commit post to database
    cur.execute("""INSERT INTO posts (userid, title, post_date, post_time, clientip, body, deleted, edited) VALUES 
                                    ('%s', '%s', '%s', '%s', '%s', "%s", false, false);""" % (userid, title, cur_date, cur_time, ip, body))
    mysql.get_db().commit()

    # Craft response
    response = jsonify({'success': True})
    return response


# delete_post: (api)
#
# Frontend "delete post" connects directly to this.
# This needs some kind of authentication
#
@post_app.route('/post/delete', methods=['POST'])
def delete_post():
    # Get user inputs
    userid = request.form.get('userid')
    postid = request.form.get('postid')

    # Get automatic inputs

    # Cursor
    cur = mysql.get_db().cursor()

    # Commit change to database
    cur.execute("""UPDATE posts 
                        SET deleted = true 
                        WHERE userid = '%s' AND postid = '%s';
                    """ % (userid, postid))
    mysql.get_db().commit()

    # Craft response
    response = jsonify({'success': True})
    return response


# edit_post: (api)
# 
# Frontend "edit post" connects directly to this.
# Lol this requires some kind of submission authentication
#
@post_app.route('/post/edit', methods=['POST'])
def edit_post():
    # Get user inputs
    postid = request.form.get('postid')
    body = request.form.get('body').replace("\"","''")  # This is very patchy

    # Cursor
    cur = mysql.get_db().cursor()

    # Commit post to database
    cur.execute("""UPDATE posts 
                        SET body = "%s",
                            edited = true
                        WHERE postid = "%s";
                """ % (body, postid))
    mysql.get_db().commit()

    # Craft response
    response = jsonify({'success': True})
    return response


# This is for testing the api. Realistically, you should use Postman
@post_app.route('/test-post', methods=['GET'])
def form():

    return '''
            <h2>Test create post</h2>
            <p>This is to create a new post</p>
            <form method="POST" action="/post/create">
                userid: <input type="text" name="userid"><br>
                title: <input type="text" name="title"><br>
                body: <input type="text" name="body"><br>
                <input type="submit" value="Submit"><br>
            </form><br>

            <h2>Test delete post</h2>
            <form method="POST" action="/post/delete">
                userid: <input type="text" name="userid"><br>
                postid: <input type="text" name="postid"><br>
                <input type="submit" value="Submit"><br>
            </form><br>

            <h2>Test edit post</h2>
            <p>This is to edit an existing post</p>
            <form method="POST" action="/post/edit">
                postid: <input type="text" name="postid"><br>
                new body: <input type="text" name="body"><br>
                <input type="submit" value="Submit"><br>
            </form><br>
            '''