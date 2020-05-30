from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, Length, AnyOf
import os
import json

SCHEMA_PATH = os.path.abspath('./app/static/form_schema.json')

class ActionForm(FlaskForm):
    pass

class BaseBotForm(FlaskForm):

    VALID_BOT_TYPES = ['economy']

    bot_pair_selection_options = [(bot_type, bot_type.title()) for bot_type in VALID_BOT_TYPES]
    bot_pair_selection_options.insert(0, (None, 'Select Type'))

    username = StringField('Reddit Username', validators=[DataRequired()])
    password = PasswordField('Reddit Password', validators=[DataRequired()])
    client_id = PasswordField('Client ID', validators=[DataRequired()])
    client_secret = PasswordField('Client Secret', validators=[DataRequired()])
    handler = SelectField('Bot Type', choices=bot_pair_selection_options, default=0, validators=[DataRequired(), AnyOf(values=VALID_BOT_TYPES)])
    submit = SubmitField('Create')

class EditEconomyBotForm(FlaskForm):

    HANDLER_CONTAINER = 'economy_commands'

    command_container = HiddenField('command_container', default=HANDLER_CONTAINER)
    submit = SubmitField('Update')

class ActionFormLoader:
    def __init__(self, form):
        self.form = form
        self.HANDLER_CONTAINER = form.HANDLER_CONTAINER

    def load_action_fields(self):
        with open(SCHEMA_PATH) as file:
            json_file = json.load(file)
            schema = json_file[self.HANDLER_CONTAINER]

        for function in schema:
            function_subform = ActionForm

            setattr(function_subform, 'function_name', StringField(function['function_name']))
            setattr(self.form, function['function_name'], FieldList(FormField(function_subform)))
