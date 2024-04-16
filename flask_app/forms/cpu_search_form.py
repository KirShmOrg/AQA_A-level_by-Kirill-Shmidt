from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField
from wtforms.validators import DataRequired

class CpuSearch(FlaskForm):
    cpu_name = SearchField(label='Find your CPU', validators=[DataRequired()])
    submit = SubmitField(label='Submit')
