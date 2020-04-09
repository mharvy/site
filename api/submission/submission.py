# submission.py

from flask import Blueprint
from flask import Flask, request, render_template, jsonify, make_response, g
from string import ascii_letters, digits
from datetime import datetime
from models import Submission, User
from app import db, auth


submission_app = Blueprint('submission_app', __name__)


@submission_app.route('/api/submission/create', methods=['POST'])
@auth.login_required
def create_submission():
    # Get user inputs
    title = request.form.get('title')
    body = request.form.get('body')
    if None in [title, body]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Get automatic inputs (ip, date, time, location)
    ip = request.remote_addr
    cur_time = datetime.now().strftime("%H:%M:%S")
    cur_date = datetime.now().strftime("%Y-%m-%d")

    # Add new submission to the database
    try:
        new_submission = Submission(userid=g.user.id,
                                        date_made=cur_date,
                                        time_made=cur_time,
                                        clientip=ip,
                                        title=title,
                                        body=body,
                                        deleted=False,
                                        edited=False,
                                        likes=0,
                                        dislikes=0,
                                        views=0)
        db.session.add(new_submission)
        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Submission added.'}))
    return response


@submission_app.route('/api/submission/remove', methods=['POST'])
@auth.login_required
def remove_submission():
    # Get user inputs
    submissionid = request.form.get('id')
    if None in [submissionid,]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Get automatic inputs

    # Mark submission as deleted in database
    # May have to actually replace title and body
    try:
        submission = Submission.query.filter_by(userid=g.user.id).\
                                      filter_by(id=submissionid).first()
        submission.deleted = True
        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Submission removed.'}))
    return response


@submission_app.route('/api/submission/edit', methods=['POST'])
@auth.login_required
def edit_submission():
    # Get user inputs
    submissionid = request.form.get('id')
    body = request.form.get('body')
    if None in [submissionid, body]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Get automatic inputs

    # Edit submission and mark as edited
    try:
        submission = Submission.query.filter_by(userid=g.user.id).\
                                      filter_by(id=submissionid).first()
        submission.edited = True
        submission.body = body
        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    response = make_response(jsonify({'status': 'success', 
                                      'message': 'Submission edited.'}))
    return response


@submission_app.route('/api/submission/like', methods=['POST'])
@auth.login_required
def like_submission():
    liked_flag = False  # Flag for if submission already liked

    # Get user inputs 
    submissionid = request.form.get('id')
    if None in [submissionid,]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Increment submission likes and add to user's liked submissions
    try:
        # First check if already liked
        u = User.query.filter_by(id=g.user.id).first()
        s_liked = [int(i) for i in u.s_liked.split(',')[:-1]]

        s = Submission.query.filter_by(id=submissionid).first()
        if s.id in s_liked:
            liked_flag = True

        # Now actually alter database
        if not liked_flag:
            s.likes = Submission.likes + 1  # No race condition
            u.s_liked = User.s_liked + str(s.id) + ','
        else:
            s.likes = Submission.likes - 1
            s_liked.remove(s.id)
            u.s_liked = ','.join(str(i) for i in s_liked)[1:]

        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    if not liked_flag:
        response = make_response(jsonify({'status': 'success', 
                                          'message': 'Submission liked.'}))
    else:
        response = make_response(jsonify({'status': 'success', 
                                          'message': 'Submission unliked.'}))
    return response


@submission_app.route('/api/submission/dislike', methods=['POST'])
@auth.login_required
def dislike_submission():
    disliked_flag = False  # Flag for if submission already disliked

    # Get user inputs 
    submissionid = request.form.get('id')
    if None in [submissionid,]:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Bad request.'}))
        return response

    # Increment submission likes and add to user's disliked submissions
    try:
        # First check if already disliked
        u = User.query.filter_by(id=g.user.id).first()
        s_disliked = [int(i) for i in u.s_disliked.split(',')[:-1]]

        s = Submission.query.filter_by(id=submissionid).first()
        if s.id in s_disliked:
            disliked_flag = True

        # Now actually alter database
        if not disliked_flag:
            s.dislikes = Submission.dislikes + 1  # No race condition
            u.s_disliked = User.s_disliked + str(s.id) + ','
        else:
            s.dislikes = Submission.dislikes - 1
            s_disliked.remove(s.id)
            u.s_disliked = ','.join(str(i) for i in s_disliked)[1:]

        db.session.commit()
    except:
        response = make_response(jsonify({'status': 'failed', 
                                          'message': 'Something went wrong.'}))
        return response

    # Craft and send response
    if not disliked_flag:
        response = make_response(jsonify({'status': 'success', 
                                          'message': 'Submission disliked.'}))
    else:
        response = make_response(jsonify({'status': 'success', 
                                          'message': 'Submission undisliked.'}))
    return response


# This is for testing the api
@submission_app.route('/api/submission/test', methods=['GET'])
@auth.login_optional
def form():

    if g.user:
        user = g.user.username
        
        submissions = Submission.query.filter_by(userid=g.user.id).all()
        submission = submissions[-1] if len(submissions) else None
        if submission:
            s_id = submission.id
            title = submission.title
            body = submission.body
            likes = str(submission.likes)
            dislikes = str(submission.dislikes)
        else:
            s_id = "None"
            title = "None"
            body = "None"
            likes = "None"
            dislikes = "None"
    else:
        s_id = "None"
        user = "None"
        title = "None"
        likes = "None"
        dislikes = "None"
        body = "None"

    return '''
            <h2>Signed in as %s</h2><br><br>
            <p>Here is your last submission:</p>
            <p>ID: %s</p>
            <p>TITLE: %s</p>
            <p>LIKES/DISLIKES: %s/%s</p>
            <p>BODY: %s<p>

            <h2>Test create submission</h2>
            <form method="POST" action="/api/submission/create">
                title: <input type="text" name="title"><br>
                body: <input type="text" name="body"><br>
                <input type="submit" value="Create submission"><br>
            </form><br>

            <h2>Test remove submission</h2>
            <form method="POST" action="/api/submission/remove">
                submission id: <input type="text" name="id"><br>
                <input type="submit" value="Remove submission"><br>
            </form><br>

            <h2>Test edit submission</h2>
            <form method="POST" action="/api/submission/edit">
                submission id: <input type="text" name="id"><br>
                new body: <input type="text" name="body"><br>
                <input type="submit" value="Edit submission"><br>
            </form><br>

            <h2>Test like submission</h2>
            <form method="POST" action="/api/submission/like">
                submission id: <input type="text" name="id"><br>
                <input type="submit" value="Like submission"><br>
            </form><br>

            <h2>Test dislike submission</h2>
            <form method="POST" action="/api/submission/dislike">
                submission id: <input type="text" name="id"><br>
                <input type="submit" value="Dislike submission"><br>
            </form><br>
            ''' % (user, s_id, title, likes, dislikes, body)
