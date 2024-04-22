from flask import render_template, redirect, url_for, flash

from flask_app import app
from class_database import db, Components, FindBy
from flask_app.forms.search_form import SearchForm


@app.route('/find-all/<component_type>/<component_name>')
def find_all_components_by_name(component_type: str, component_name: str):
    component = Components(component_type)
    component_list = db.get_one_component_list(component, by=FindBy.SearchStr, value=component_name)
    if component == Components.CPU:
        return render_template('components/cpu_list.html', cpu_list=component_list)
    elif component == Components.GPU:
        return render_template('components/gpu_list.html', gpu_list=component_list)
    elif component == Components.MB:
        return render_template('components/mb_list.html', mb_list=component_list)
    elif component == Components.RAM:
        return render_template('components/ram_list.html', ram_list=component_list)
    elif component == Components.PSU:
        return render_template('components/psu_list.html', psu_list=component_list)
    else:
        flash(f"Can't fetch {component_type}", "error")
        return redirect(url_for('index'))


@app.route('/find-all/<component_type>', methods=['get', 'post'])
def specific_component_page(component_type: str):
    component = Components(component_type)
    form = SearchForm()
    if form.validate_on_submit():
        search_str = form.name.data
        return redirect(url_for('find_all_components_by_name', component_type=component.value, component_name=search_str))
    if component == Components.CPU:
        return render_template('components/cpu_filters.html', search_form=form)
