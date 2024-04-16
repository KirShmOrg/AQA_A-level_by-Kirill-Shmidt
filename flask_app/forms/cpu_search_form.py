from flask_wtf import FlaskForm
from wtforms import SearchField, SubmitField

class CpuSearch(FlaskForm):
    cpu_name = SearchField(label='Find your CPU')
    submit = SubmitField(label='Submit')
