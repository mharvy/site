# comment.py

from flask import Blueprint
from flask import Flask, request, render_template, jsonify, make_response, g
from string import ascii_letters, digits
from datetime import datetime
from models import Comment, User
from app import db, auth


comment_app = Blueprint('comment_app', __name__)


@comment_app.route('/api/comment/create', methods=['POST'])
@auth.login_required
def create_comment():
    # Get user inputs
    submissionid = request.form.get('submissionid')
    parent_comment = request.form.get('parent_comment')
    body = request.form.get('body')
    if None in [submissionid, parent_comment, body]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Get automatic inputs (ip, date, time, location)
    ip = request.remote_addr
    cur_time = datetime.now().strftime("%H:%M:%S")
    cur_date = datetime.now().strftime("%Y-%m-%d")

    # Add new submission to the database
    try:
        new_comment = Comment(submissionid=submissionid,
                              userid=g.user.id,
                              parent_comment=parent_comment,
                              date_made=cur_date,
                              time_made=cur_time,
                              clientip=ip,
                              body=body,
                              deleted=False,
                              edited=False,
                              likes=0,
                              dislikes=0)
        db.session.add(new_comment)
        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Comment added.'}))
    return response


@comment_app.route('/api/comment/remove', methods=['POST'])
@auth.login_required
def remove_comment():
    # Get user inputs
    commentid = request.form.get('id')
    if None in [commentid,]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Get automatic inputs

    # Mark comment as deleted in database
    # May have to actually replace title and body
    try:
        comment = Comment.query.filter_by(userid=g.user.id).\
                                filter_by(id=commentid).first()
        comment.deleted = True
        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Comment removed.'}))
    return response


@comment_app.route('/api/comment/edit', methods=['POST'])
@auth.login_required
def edit_comment():
    # Get user inputs
    commentid = request.form.get('id')
    body = request.form.get('body').replace("\"","''")  # This is very patchy
    if None in [commentid, body]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Get automatic inputs

    # Edit comment and mark as edited
    try:
        comment = Comment.query.filter_by(userid=g.user.id).\
                                   filter_by(id=commentid).first()
        comment.edited = True
        comment.body = body
        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Comment edited.'}))
    return response


@comment_app.route('/api/comment/like', methods=['POST'])
@auth.login_required
def like_comment():
    liked_flag = False  # Flag for if comment already liked

    # Get user inputs 
    commentid = request.form.get('id')
    if None in [commentid,]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Increment comment likes and add to user's liked comments
    try:
        # First check if already liked
        u = User.query.filter_by(id=g.user.id).first()
        c_liked = [int(i) for i in u.c_liked.split(',')[:-1]]

        c = Comment.query.filter_by(id=commentid).first()
        if c.id in c_liked:
            liked_flag = True

        # Now actually alter database
        if not liked_flag:
            c.likes = Comment.likes + 1  # No race condition
            u.c_liked = User.c_liked + str(c.id) + ','
        else:
            c.likes = Comment.likes - 1
            c_liked.remove(c.id)
            u.c_liked = ','.join(str(i) for i in c_liked)[1:]

        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    if not liked_flag:
        response = make_response(jsonify({'status': 'success', 
                                          'message': 'Comment liked.'}))
    else:
        response = make_response(jsonify({'status': 'success', 
                                          'message': 'Comment unliked.'}))
    return response


@comment_app.route('/api/comment/dislike', methods=['POST'])
@auth.login_required
def dislike_comment():
    disliked_flag = False  # Flag for if comment already disliked

    # Get user inputs 
    commentid = request.form.get('id')
    if None in [commentid,]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Increment comment likes and add to user's disliked comments
    try:
        # First check if already disliked
        u = User.query.filter_by(id=g.user.id).first()
        c_disliked = [int(i) for i in u.c_disliked.split(',')[:-1]]

        c = Comment.query.filter_by(id=commentid).first()
        if c.id in c_disliked:
            disliked_flag = True

        # Now actually alter database
        if not disliked_flag:
            c.dislikes = Comment.dislikes + 1  # No race condition
            u.c_disliked = User.c_disliked + str(c.id) + ','
        else:
            c.dislikes = Comment.dislikes - 1
            c_disliked.remove(s.id)
            u.c_disliked = ','.join(str(i) for i in c_disliked)[1:]

        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    if not disliked_flag:
        response = make_response(jsonify({'status': 'success', 
                                          'message': 'Comment disliked.'}))
    else:
        response = make_response(jsonify({'status': 'success', 
                                          'message': 'Comment undisliked.'}))
    return response


# This is for testing the api
@comment_app.route('/api/comment/test', methods=['GET'])
@auth.login_optional
def form():

    if g.user:
        user = g.user.username
        
        comments = Comment.query.filter_by(userid=g.user.id).all()
        comment = comments[-1] if len(comments) else None 
        if comment:
            c_id = comment.id
            body = comment.body
            likes = str(comment.likes)
            dislikes = str(comment.dislikes)
        else:
            c_id = "None"
            likes = "None"
            dislikes = "None"
            body = "None"
    else:
        c_id = "None"
        user = "None"
        likes = "None"
        dislikes = "None"
        body = "None"

    return '''
            <h2>Signed in as %s</h2><br><br>
            <p>Here is your last comment:</p>
            <p>ID: %s</p>
            <p>LIKES/DISLIKES: %s/%s</p>
            <p>BODY: %s</p>

            <h2>Test create comment</h2>
            <form method="POST" action="/api/comment/create">
                submissionid: <input type="text" name ="submissionid"><br>
                parent_comment: <input type="text" name="parent_comment"><br>
                body: <input type="text" name="body"><br>
                <input type="submit" value="Create comment"><br>
            </form><br>

            <h2>Test remove comment</h2>
            <form method="POST" action="/api/comment/remove">
                comment id: <input type="text" name="id"><br>
                <input type="submit" value="Remove comment"><br>
            </form><br>

            <h2>Test edit comment</h2>
            <form method="POST" action="/api/comment/edit">
                comment id: <input type="text" name="id"><br>
                new body: <input type="text" name="body"><br>
                <input type="submit" value="Submit"><br>
            </form><br>

            <h2>Test like comment</h2>
            <form method="POST" action="/api/comment/like">
                submission id: <input type="text" name="id"><br>
                <input type="submit" value="Like comment"><br>
            </form><br>

            <h2>Test dislike comment</h2>
            <form method="POST" action="/api/comment/dislike">
                submission id: <input type="text" name="id"><br>
                <input type="submit" value="Dislike comment"><br>
            </form><br>
            ''' % (user, c_id, likes, dislikes, body)
