from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField, SelectField
from wtforms.validators import DataRequired

from class_database import Components


class ComponentSearch(FlaskForm):
    component = SelectField(label='Type of component', choices=[i.value for i in list(Components)])
    name = SearchField(label='Find component by name', validators=[DataRequired()])
    submit = SubmitField(label='Submit')
