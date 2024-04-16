from flask import render_template, redirect
from wrappers import measure_time

from flask_app import app
from ..forms.component_search_form import ComponentSearch


@measure_time
@app.route('/', methods=["GET", "POST"])
def index():
    form = ComponentSearch()
    if form.validate_on_submit():
        component_type = form.component.data
        component_name = form.name.data
        return redirect(f'/find-all/{component_type}/{component_name}')
    return render_template('home/index.html', search_form=form)
