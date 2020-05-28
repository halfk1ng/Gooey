from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, AnyOf

class BaseBotForm(FlaskForm):

    VALID_BOT_TYPES = ['economy']

    bot_pair_selection_options = [(bot_type, bot_type.title()) for bot_type in VALID_BOT_TYPES]
    bot_pair_selection_options.insert(0, (None, 'Select Type'))

    username = StringField('Reddit Username', validators=[DataRequired()])
    password = PasswordField('Reddit Password', validators=[DataRequired()])
    client_id = PasswordField('Client ID', validators=[DataRequired()])
    client_secret = PasswordField('Client Secret', validators=[DataRequired()])
    bot_type = SelectField('Bot Type', choices=bot_pair_selection_options, default=0, validators=[DataRequired(), AnyOf(values=VALID_BOT_TYPES)])
    submit = SubmitField('Create')