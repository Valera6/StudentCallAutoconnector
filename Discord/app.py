from config import *
from talk_to_discord import wait_for_the_call
from flask import Flask, render_template, request, session, redirect
from zenora import APIClient
import json, os
from datetime import datetime

def oauth_site(start_time, timezone):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'verysecret'
    client = APIClient(TOKEN, client_secret=CLIENT_SECRET)


    @app.route('/')
    def home():
        if 'token' in session:
            bearer_client = APIClient(session.get('token'), bearer=True)
            with open('bearer_token.json', 'w') as f:
                json.dump(session.get('token'), f)
            current_user = bearer_client.users.get_current_user()
            # call talk_to_discord module somewhere here
            return render_template('index.html', current_user=current_user, start_time=start_time, timezone=timezone)
        return render_template('index.html', oauth_url=OAUTH_URL)

    @app.route('/oauth/callback')
    def callback():
        code = request.args['code']
        access_token = client.oauth.get_access_token(code, REDIRECT_URI).access_token
        session['token'] = access_token
        return redirect('/')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect('/')

    app.run(debug=True)

if __name__ == '__main__':
    oauth_site(datetime.now(), 'UTC+0')
