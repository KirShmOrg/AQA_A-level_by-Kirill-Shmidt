from flask_app import app
from flask import render_template
from class_database import db, Components
from techpowerup import generate_link as techpowerup_link


@app.route('/cpu-list')
def show_cpu_list():
    test_params = {"mfgr": 'AMD',
                   "released": '2022',
                   "mobile": 'No',
                   "server": 'No',
                   "multiUnlocked": 'Yes'}
    print(techpowerup_link(Components.CPU, test_params))
    cpu_list = db.get_cpu_list(params=test_params)
    return render_template('components/cpu_list.html', title='Find CPUs', cpu_list=cpu_list)

@app.route('/cpu/<cpu_name>')
def show_cpu_page(cpu_name: str):
    print(cpu_name)
    raise NotImplementedError("I can't fetch a single CPU for now")
