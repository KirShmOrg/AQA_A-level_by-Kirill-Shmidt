from flask_app import app
from flask import render_template
from class_database import db, Components
from techpowerup import generate_link as techpowerup_link


@app.route('/find/cpu')
def find_cpu():
    test_params = {"mfgr": 'AMD',
                   "released": '2022',
                   "mobile": 'No',
                   "server": 'No',
                   "multiUnlocked": 'Yes'}
    print(techpowerup_link(Components.CPU, test_params))
    cpu_list = db.get_cpu_list(params=test_params)
    for cpu in cpu_list:
        print(cpu)
    return render_template('components/cpus.html', title='Find CPUs', cpu_list=cpu_list)
