import tweepy, sys, json
from flask import redirect, session, request, url_for, jsonify, Response, request
from flask.ext.login import logout_user, login_user, login_required, current_user
from neuhatch import config, app, db, login_manager
from neuhatch.models import User
from neuhatch.crossdomain import crossdomain
import neuhatch.utils as utils

@login_manager.user_loader
def load_user(userid):
    return User.query.filter_by(id=userid).first()

@app.route("/users")
@login_required
def users():
    users = User.query.all()
    out = []
    for user in users:
        out.append(user.serialize())
    return json.dumps(out)


@app.route("/oauth")
def oauth():
    try:
        # TODO: abstract callback url to config
        callback_url = "%s%s" % ("http://localhost:5000", url_for("callback"))
        # create initial tweepy callback object
        auth = utils.get_base_auth()
        # get redirect url
        redirect_url = auth.get_authorization_url()
        # set request token
        session['request_token'] = auth.request_token
        return redirect(redirect_url)
    except tweepy.TweepError as e:
        return 'Failed to get request token %s' % e
    except:
        # todo error handling
        return str(sys.exc_info())

@app.route('/callback')
def callback():
    try:
        request_token = session['request_token']
        verifier = request.args.get('oauth_verifier')
        del session['request_token']
    except:
        print("error getting auth verifier or request_token")
        # todo appropriate error handling
        return str(sys.exc_info())

    username, key, secret = utils.verify_api(request_token, verifier)

    user = User.query.filter_by(username=username).first()

    # create user if first time
    if user is None:
        user = User(username, key, secret)
        print("Creating user %s: %s" % (username, user,))
        db.session.add(user)
        db.session.commit()

    print("Logging in user %s" % user)
    login_user(user)

    return redirect(config.hostname)


@app.route('/user')
@login_required
def user():
    return str((current_user.id, current_user.access_token, current_user.access_token_secret))

@app.route('/search')
@crossdomain(origin='*')
@login_required
def search():
    # TODO: used logged in user
    user = User.query.filter_by(username="test").first()
    api = utils.get_user_api(user)
    query = request.args.get('q')
    results = api.search(q=query)
    output = []
    for result in results:
        output.append(result._json)
    out_json = json.dumps(output)

    return Response(out_json, mimetype="application/json")
