from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    name = SearchField(label='Find by name', validators=[DataRequired()])
    submit = SubmitField(label='Find')
