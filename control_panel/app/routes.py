from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import BaseBotForm, EditEconomyBotForm, ActionForm, ActionFormLoader
from app.utils import BotConfigBuilder, FormSelector, ConfigAlreadyExists

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new', methods=['GET', 'POST'])
def new():
    form = BaseBotForm()

    if form.validate_on_submit():
        try:
            BotConfigBuilder.build_new(form)
            flash('Bot configuration created successfully!', 'success')
        except ConfigAlreadyExists:
            flash('Bot configuration was not created. Existing configuration could not be overwritten.', 'danger')
            flash('If the problem persists, try deleting your existing configuration.', 'danger')
        return redirect( url_for('index') )

    return render_template('new.html', form=form)

@app.route('/edit', methods=['GET', 'POST'])
def edit():
    bot_config = BotConfigBuilder.load_bot_config()
    form = FormSelector.select_form_for_bot_type(bot_config['handler'])
    ActionFormLoader(form).load_action_fields()

    return render_template('edit.html', name='GooeyBot', form=form())

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500