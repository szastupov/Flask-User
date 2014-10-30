""" This file implements Flask-User decorators: @login_required and @roles_required.

    :copyright: (c) 2013 by Ling Thio
    :author: Ling Thio (ling.thio@gmail.com)
    :license: Simplified BSD License, see LICENSE.txt for more details."""

from functools import wraps
from flask import current_app
from flask.ext.login import current_user

def login_required(func):
    """ This decorator ensures that the current user is logged in before calling the actual view.
        Calls the unauthorized_view_function() when the user is not logged in."""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # User must be authenticated
        if not current_user.is_authenticated():
            # Redirect to unauthenticated page
            return current_app.user_manager.unauthenticated_view_function()

        # Call the actual view
        return func(*args, **kwargs)
    return decorated_view


def roles_required(*required_roles):
    """ This decorator ensures that the current user has all the required roles
        before calling the actual view.
        Calls the unauthorized_view_function() when requirements fail.

        roles_required() accepts a list of requirements:
            roles_required(requirement1, requirement2, requirement3).

        Each requirement is either a role_name, or a tuple_of_role_names.
            role_name example:   'manager'
            tuple_of_role_names: ('funny', 'witty', 'hilarious')
        A role_name-requirement is accepted when the user has this role.
        A tuple_of_role_names-requirement is accepted when the user has ONE of these roles.
        roles_required() returns true if ALL of the requirements have been accepted.

        For example:
            roles_required('a', ('b', 'c'), d)
        Translates to:
            User must have role 'a' AND (role 'b' OR role 'c') AND role 'd'"""
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            # User must be logged
            if not current_user.is_authenticated():
                # Redirect to the unauthenticated page
                return current_app.user_manager.unauthenticated_view_function()

            # User must have the required roles
            if not current_user.has_roles(*required_roles):
                # Redirect to the unauthorized page
                return current_app.user_manager.unauthorized_view_function()

            # Call the actual view
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


def confirm_email_required(func):
    """ This decorator ensures that the current user is logged in and has confirmed their email.
        Calls the unauthorized_view_function() when the user is not logged in."""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # User must be authenticated
        if current_user.is_authenticated():
            user_manager = current_app.user_manager
            # If confirm email has been enabled, user must have at least one confirmed email
            if not user_manager.enable_email\
                    or not user_manager.enable_confirm_email\
                    or current_user.has_confirmed_email():
                return func(*args, **kwargs)

        return current_app.user_manager.unconfirmed_email_view_function()

    return decorated_view


def user_has_confirmed_email(user):
    db_adapter = current_app.user_manager.db_adapter

    # Handle multiple emails per user: Find at least one confirmed email
    if db_adapter.UserEmailClass:
        has_confirmed_email = False
        print('1')
        user_emails = db_adapter.find_all_objects(db_adapter.UserEmailClass, user_id=user.id)
        for user_email in user_emails:
            print('2')
            if user_email.confirmed_at:
                print('3')
                has_confirmed_email = True
                break

    # Handle single email per user
    else:
        has_confirmed_email = True if user.confirmed_at else False

    return has_confirmed_email
