from functools import wraps

from flask import request, abort, flash, redirect, url_for
from flask_login import current_user
from flask_login.config import EXEMPT_METHODS


def super_admin_role_required(func):
    """ A decorator for checking whether a user is super admin or not"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif not current_user.is_super_admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated_view


def admin_role_required(func):
    """ A decorator for checking whether a user is admin or not"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated_view


def user_required(func):
    """ A decorator for checking whether a user is a normal user"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_user.is_admin or current_user.is_super_admin:
            abort(403)
        return func(*args, **kwargs)
    return decorated_view


def user_verified(func):
    """ A decorator for checking whether a user is verified or not"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif not current_user.is_verified:
            flash("You need to be verified first to carry on!", "info")
            return redirect(url_for('users.apply_for_verification'))
        return func(*args, **kwargs)
    return decorated_view
