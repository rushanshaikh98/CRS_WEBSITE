from flask import Blueprint, render_template
from ..main.forms import SearchForm

errors = Blueprint('errors', __name__)


@errors.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


@errors.app_errorhandler(404)
def error_404(error):
    """Method to display a good and manageable user interface for 404 Errors"""
    form = SearchForm()
    return render_template('errors/404.html', form=form), 404


@errors.app_errorhandler(403)
def error_403(error):
    """Method to display a good and manageable user interface for 403 Errors"""
    form = SearchForm()
    return render_template('errors/403.html', form=form), 403


@errors.app_errorhandler(500)
def error_500(error):
    """Method to display a good and manageable user interface for 500 Errors"""
    form = SearchForm()
    return render_template('errors/500.html', form=form), 500
