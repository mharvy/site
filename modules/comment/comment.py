# comment.py

from flask import Blueprint
from flask import Flask, request, render_template, jsonify
from string import ascii_letters, digits
from extensions import mysql
from datetime import datetime


comment_app = Blueprint('comment_app', __name__)


# create_comment: (api)
# 
# Frontend "create comment" connects directly to this.
# Lol this requires some kind of submission authentication
#
@comment_app.route('/comment/create', methods=['POST'])
def create_comment():
    # Get user inputs
    try:
        postid = request.form.get('postid')
        userid = request.form.get('userid')
        parent_comment = request.form.get('parent_comment')
        body = request.form.get('body').replace("'","\\'")  # This is very patchy
    except:
        return jsonify({'success': False})

    # Get automatic inputs (ip, date, time, location)
    ip = request.remote_addr
    cur_time = datetime.now().strftime("%H:%M:%S")
    cur_date = datetime.now().strftime("%Y-%m-%d")

    # Cursor
    cur = mysql.get_db().cursor()

    # Commit post to database
    cur.execute("""INSERT INTO comments (postid, userid, parent_comment, post_date, post_time, clientip, body, deleted, edited) 
                   VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', false, false);""" % (postid, userid, parent_comment, cur_date, cur_time, ip, body))
    mysql.get_db().commit()

    # Craft response
    return jsonify({'success': True})


# delete_comment: (api)
#
# Frontend "delete comment" connects directly to this.
# This needs some kind of authentication
#
@comment_app.route('/comment/delete', methods=['POST'])
def delete_comment():
    # Get user inputs
    try:
        userid = request.form.get('userid')
        commentid = request.form.get('commentid')
    except:
        return jsonify({'success': False})

    # Get automatic inputs

    # Cursor
    cur = mysql.get_db().cursor()

    # Commit change to database
    cur.execute("""UPDATE comments
                        SET deleted = true 
                        WHERE userid = '%s' AND commentid = '%s';
                    """ % (userid, commentid))
    mysql.get_db().commit()

    # Craft response
    return jsonify({'success': True})


# edit_comment: (api)
# 
# Frontend "edit comment" connects directly to this.
# Lol this requires some kind of submission authentication
#
@comment_app.route('/comment/edit', methods=['POST'])
def edit_comment():
    # Get user inputs
    try:
        commentid = request.form.get('commentid')
        body = request.form.get('body').replace("\"","''")  # This is very patchy
    except:
        return jsonify({'success': False})

    # Cursor
    cur = mysql.get_db().cursor()

    # Commit post to database
    cur.execute("""UPDATE comments 
                        SET body = "%s",
                            edited = true
                        WHERE commentid = "%s";
                """ % (body, commentid))
    mysql.get_db().commit()

    # Craft response
    return jsonify({'success': True})


# This is for testing the api. Realistically, you should use Postman
@comment_app.route('/comment/test', methods=['GET'])
def form():

    return '''
            <h2>Test create comment</h2>
            <p>This is to create a new comment</p>
            <form method="POST" action="/comment/create">
                postid: <input type="text" name ="postid"><br>
                userid: <input type="text" name="userid"><br>
                parent_comment: <input type="text" name="parent_comment"><br>
                body: <input type="text" name="body"><br>
                <input type="submit" value="Submit"><br>
            </form><br>

            <h2>Test delete comment</h2>
            <form method="POST" action="/comment/delete">
                userid: <input type="text" name="userid"><br>
                commentid: <input type="text" name="commentid"><br>
                <input type="submit" value="Submit"><br>
            </form><br>

            <h2>Test edit comment</h2>
            <p>This is to edit an existing comment</p>
            <form method="POST" action="/comment/edit">
                commentid: <input type="text" name="commentid"><br>
                new body: <input type="text" name="body"><br>
                <input type="submit" value="Submit"><br>
            </form><br>
            '''