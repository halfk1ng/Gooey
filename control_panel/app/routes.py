from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import BaseBotForm

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new', methods=['GET', 'POST'])
def new():
    form = BaseBotForm()

    if form.validate_on_submit():
        flash('Bot created successfully!', 'success')
        return redirect( url_for('index') )

    return render_template('new.html', form=form)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500