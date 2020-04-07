# submission.py

from flask import Blueprint
from flask import Flask, request, render_template, jsonify, make_response, g
from string import ascii_letters, digits
from datetime import datetime
from models import Submission
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
                                    like=0,
                                    dislike=0,
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
    if None in [postid,]:
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
        liked = [int(i) for i in u.liked.split(",")]

        s = Submission.query.filter_by(id=submissionid).first()
        if s.id in liked:
            liked_flag = True

        # Now actually alter database
        if not liked_flag:
            s.likes = Submission.likes + 1  # No race condition
            u.liked = User.liked + str(s.id) + ","
        else:
            s.likes = Submission.likes + 1
            u.liked = ','.join(str(i) for i in liked.remove(s.id))

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
        disliked = [int(i) for i in u.disliked.split(",")]

        s = Submission.query.filter_by(id=submissionid).first()
        if s.id in disliked:
            disliked_flag = True

        # Now actually alter database
        if not disliked_flag:
            s.likes = Submission.likes + 1  # No race condition
            u.disliked = User.disliked + str(s.id) + ","
        else:
            s.likes = Submission.likes + 1
            u.disliked = ','.join(str(i) for i in disliked.remove(s.id))

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
        else:
            s_id = "None"
            title = "None"
            body = "None"
    else:
        s_id = "None"
        user = "None"
        title = "None"
        body = "None"

    return '''
            <h2>Signed in as %s<h2><br><br>
            <p>Here is your last submission:</p>
            <h3>%s: %s</h3>
            <p>%s<p>

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
            ''' % (user, s_id, title, body)
