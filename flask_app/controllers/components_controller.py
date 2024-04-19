from flask import render_template, redirect, url_for, flash

from flask_app import app
from class_database import db, Components, FindBy


@app.route('/find-all/<component_type>/<component_name>')
def find_all_components_by_name(component_type: str, component_name: str):
    component = Components(component_type)
    component_list = db.get_one_component_list(component, by=FindBy.SearchStr, value=component_name)
    if component == Components.CPU:
        return render_template('components/cpu_list.html', cpu_list=component_list)
    elif component == Components.GPU:
        return render_template('components/gpu_list.html', gpu_list=component_list)
    elif component == Components.RAM:
        return render_template('components/ram_list.html', ram_list=component_list)
    else:
        flash(f"Can't fetch {component_type}", "error")
        return redirect(url_for('index'))
