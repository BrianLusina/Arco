from . import auth
from app import db
from flask_login import current_user
from .security import generate_confirmation_token, confirm_token, send_mail_async
from flask import jsonify, request, redirect, url_for, abort, render_template
from app import db
from .forms import ResetPasswordForm
import requests
from datetime import datetime
from flask_login import current_user, login_user, logout_user, login_required
from .models import UserProfile, UserAccount, UserAccountStatus, FacebookAccount


@auth.route("register", methods=["GET", "POST"])
def register():
    """
    Registers a new user, get request data, parse it and register user accordingly
    successful registration of user will store data in db and send back a response to client
    informing user to confirm their email account. (An email will be sent for confirmation)
    Thus, afterwards, the user will then confirm their email and the client will then
     redirect user to login and they can proceed to login with their registered credentials
    :return: JSON response of the registering user process
    """
    # if the data from request values is available, perform data transaction
    if request.method == "POST":
        email = request.values.get("email")
        user_account = UserAccount.query.filter_by(email=email).first()

        # check if the user already exists
        if user_account is not None:
            # return registration failed message back to client
            return jsonify(dict(response=400, message="User already exists"))
        else:
            # create the new user and store values in dict
            email = request.values.get("email")
            first_name = request.values.get("first_name")
            last_name = request.values.get("last_name")
            username = request.values.get("username")
            password = request.values.get("password")

            # create a new user profile
            new_user_profile = UserProfile(
                email=email,
                first_name=first_name,
                last_name=last_name,
                accept_tos=True,
            )

            # add the new user profile and commit
            db.session.add(new_user_profile)
            db.session.commit()

            # now we add the status of this new account and commit it
            new_user_account_status = UserAccountStatus(code="0", name="EMAIL_NON_CONFIRMED")

            db.session.add(new_user_account_status)
            db.session.commit()

            # add the new user account and commit it
            new_user_account = UserAccount(
                email=email,
                username=username,
                password=password,
                user_profile_id=new_user_profile.id,
                user_account_status_id=new_user_account_status.id
            )

            db.session.add(new_user_account)
            db.session.commit()

            # create a token from the new user account
            token = new_user_account.generate_confirm_token()

            # _external adds the full absolute URL that includes the hostname and port
            confirm_url = url_for("auth.confirm_email", token=token, _external=True)

            # send user confirmation email asynchronously
            # Todo: fails to send email, why?
            send_mail_async.delay(new_user_account.email, "Please Confirm you email",
                                  "auth.confirm_email.html", confirm_url)

            # log in the new user
            login_user(new_user_account)

            # post a success message back to client so that the client can redirect user
            # to login
            return jsonify(dict(status="success", message="User created",
                                state="User Logged in", response=200,
                                confirm_email_sent=True))

    elif request.method == "GET":
        return jsonify(dict())
    return jsonify(dict())


@auth.route('confirm/<token>')
# @login_required
def confirm_email(token):
    """
    Confirm email route for the user. 
    Checks if the user has already confirmed their account
    If they have, log them in. If they have not, 
    confirm their account and direct them to their dashboard we call the confirm_token()
     function, passing in the token. If successful, we update the user,
    changing the email_confirmed attribute to True and setting the datetime for when the 
    confirmation took place.
    Also, in case the user already went through the confirmation process – and is
     confirmed – then we alert the user of this.
    :param token: Generated in the user registration
    :return: A redirect to login
    """

    # if the current user had been confirmed, redirect them to login
    if current_user.confirmed:
        return redirect(url_for('auth.login'))

    # else confirm them
    # get the email for the confirmed
    email = confirm_token(token)

    # get the author or throw an error
    user = UserAccount.query.filter_by(email=current_user.email).first_or_404()

    if user.email == email:
        user.confirmed = True
        user.confirmed_on = datetime.now()

        # update the confirmed_on column
        db.session.add(user)
        db.session.commit()

        # redirect to login
        return redirect(url_for('auth.login'))
    else:
        pass
    # redirect to the user's dashboard
    return redirect(url_for('auth.login'))


@auth.route("login", methods=["GET", "POST"])
def login():
    pass


@auth.route("signup", methods=["GET", "POST"])
def signup():
    pass
    if request.method == "POST":
        # if request is POST, retrieve data and log in the user
        user_email = request.values.get("email")
        user_password = request.values.get("password")

        # get the user object and check if they exist
        user = UserAccount.query.filter_by(email=user_email).first()

        # if the user exists, check their password
        if user is not None:
            if user.verify_password(user_password):
                # log in the user
                login_user(user)

                # return response to client
                return jsonify(dict(message="Logged in success", success=True, response_code=200))
            else:
                # wrong password, return error message to client
                return jsonify(dict(message="Log in Failure", success=False, response_code=400,
                                    cause="Wrong password"))
        else:
            # this user does not exist
            return jsonify(dict(message="User does not exist", success=False, response_code=400))
    return jsonify(dict())


@auth.route("reset", methods=["GET", "POST"])
def reset_password():
    """
    Resets the user's password if they have forgotten it. In this case, we shall get the user email
    and send a confirmation link to the given email. This, in turn, will let us know that the user
    exists, because they will then click on the url in their email and be given instructions on
    resetting the user password
    :return: Response to user stating that their new password has been sent to their email
    """
    if request.method == "POST":
        # get email from request
        email = request.values.get("email")

        # generate token
        token = generate_confirmation_token(email)

        # create the recover url to be sent in the email
        recover_url = url_for("auth.reset_with_token", token=token, _external=True)

        # send user confirmation email asynchronously
        # Todo: fails to send email, why?
        send_mail_async.delay(email, "Please reset requested", "auth.reset_email.html", recover_url)

        return jsonify(dict(message="Password reset sent", success=True))

    return jsonify(dict())


@auth.route("reset_password/<token>")
def reset_with_token(token):
    """
    Resets the user account with the given token they will get from the url given in their email
    :param token: random secure token user will get in their email address
    :return:
    """
    # get the email for user to reset their account
    email = confirm_token(token)

    if email is None:
        abort(404)

    form = ResetPasswordForm(request.form)

    if form.validate_on_submit():
        # get the author or throw an error
        user = UserAccount.query.filter_by(email=email).first_or_404()

        user.password = form.password.data

        user.confirmed = True
        user.confirmed_on = datetime.now()

        # update the confirmed_on column
        db.session.add(user)
        db.session.commit()

        # todo: redirect to client login page
        return redirect(url_for('auth.login'))
    # render this template
    return render_template('auth.reset_with_token.html', form=form)


@auth.route("facebook", methods=["GET", "POST"])
def login_with_facebook():
    """
    Login user with facebook
    """
    pass


@auth.route("google", methods=["GET", "POST"])
def login_with_google():
    """
    Login user with facebook
    """
    pass


@auth.route("twitter", methods=["GET", "POST"])
def login_with_twitter():
    """
    Login user with facebook
    """
    pass


@auth.route("logout")
@login_required
def logout():
    """
    Logs out the user from server session
    :return: json response
    :rtype: dict
    """
    logout_user()
    return jsonify(dict(message="User logged out", success=True))
