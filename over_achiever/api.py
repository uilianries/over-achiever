import os

from flask import Flask, url_for, session, jsonify
from flask.ext.oauthlib.client import OAuth
from flask.ext.sqlalchemy import SQLAlchemy
from flask_restful import Api, abort
from over_achiever import models
from over_achiever import resources
from over_achiever.resources import User, Goal


def create_app():
    app = Flask(__name__)
    app.config.from_object('over_achiever.config')
    db = SQLAlchemy(app, metadata=models.metadata)
    db.create_all()
    resources.db = app.db = db

    oauth = OAuth(app)
    google = oauth.remote_app(
        'google',
        consumer_key=os.getenv("GOOGLE_CLIENT_ID", ""),
        consumer_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
        request_token_params={
            'scope': 'email'
        },
        base_url='https://www.googleapis.com/oauth2/v1/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        authorize_url='https://accounts.google.com/o/oauth2/auth',
    )

    # set the token getter for the auth client
    google._tokengetter = lambda: session.get('google_token')
    resources.google = app.google = google

    api = Api(app)
    resource_map = (
        (User, '/v1.0/users'),
        (Goal, '/v1.0/goals'),
    )

    for resource, route in resource_map:
        api.add_resource(resource, route)

    return app

app = create_app()


@app.route('/login')
def login():
    return app.google.authorize(callback=url_for('authorized',
                                                 _external=True))


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return 'OK'


@app.route('/login/authorized')
def authorized():
    resp = app.google.authorized_response()
    if resp is None:
        # return 'Access denied: reason=%s error=%s' % (
        #     request.args['error'],
        #     request.args['error_description']
        # )
        abort(401, message='Access denied!')
    app.logger.info("RESP: %s" % resp)
    token = resp['access_token']
    # Must be in a list or tuple because github auth code extracts the first
    user = app.google.get('userinfo', token=[token])
    app.logger.info("USER: %s" % str(user))
    user.data['access_token'] = token
    return jsonify(user.data)
